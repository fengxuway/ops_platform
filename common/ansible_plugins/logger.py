#!/usr/bin/env python
# coding=utf-8
from ansible import utils
from ansible.module_utils import basic
from service.models import Service
from server.models import Server
from service.logic import ansible_ip
from service.logic import run_task
import configparser
# This message will get concatenated to until it's time
# to log "flush" the message to the database


log_message = []


def banner(msg):
    """Output Trailing Stars"""
    width = 78 - len(msg)
    if width < 3:
        width = 3
    filler = "*" * width
    return "\n%s %s " % (msg, filler)


def append_to_log(msg):
    """Append message to log_message"""
    global log_message
    log_message.append(msg)


def flush_to_database(has_errors=False, stats=None, playbook=None):
    """Save log_message to database"""
    global log_message
    log_type = 'info'
    if has_errors:
        log_type = 'error'

    # 这里仅适用于安装部署服务
    if playbook and hasattr(playbook, 'service_ids'):
        srvs = Service.objects.filter(id__in=playbook.service_ids)
        print("srvs :::", srvs)
        srvs.update(install_log='\n'.join(log_message))

        # 检测nginx_php_memcache镜像包是否安装成功
        srv_nginx = srvs[0].service_name
        srv_id = srvs[0].server_id
        srv_odj = srvs[0]  # 取出server的对象
        print("srv_ojb", srv_odj)
        if srv_nginx == "nginx_php_memcache":
            print("srv_nginx", srv_nginx)

            c_path = srv_odj.config_path if srv_odj.config_path else srv_odj.image.config_path
            print("c_pach:::", c_path)
            cf = configparser.ConfigParser()
            cf.read(c_path)  # 读取配置文件

            # 取出检测nginx镜像安装状态脚本
            c_check_status_cmd = cf.get("operation", "check_rpm_install_status")
            rem_host = Server.objects.filter(id=srv_id)[0].ansible_host  # 取出remote_host
            rem_ip = ansible_ip(rem_host)  # 取出远程主机IP
            # 检测服务
            status_result = run_task([rem_host], module_args=c_check_status_cmd)
            s_result = status_result[rem_ip]['result']['stdout']
            if 'install nginx php memcache ok' in s_result:  # 判断服务是否启动
                if has_errors:
                    srvs.update(state=-1)
                else:
                    srvs.update(state=1)
            else:

                print("install nginx php memcache faild !")
        else:
            if has_errors:
                srvs.update(state=-1)
            else:
                srvs.update(state=1)
    else:
        print("Playbook is None")


class CallbackModule(object):
    """
    An ansible callback module for saving Ansible output to a database log
    """

    def runner_on_failed(self, host, res, ignore_errors=False):
        results2 = res.copy()
        results2.pop('invocation', None)

        item = results2.get('item', None)

        if item:
            msg = "failed: [%s] => (item=%s) => %s" % (host, item, utils.jsonify(results2))
        else:
            msg = "failed: [%s] => %s" % (host, utils.jsonify(results2))

        append_to_log(msg)

    def runner_on_ok(self, host, res):
        results2 = res.copy()
        results2.pop('invocation', None)

        item = results2.get('item', None)

        changed = results2.get('changed', False)
        ok_or_changed = 'ok'
        if changed:
            ok_or_changed = 'changed'

        msg = "%s: [%s] => (item=%s)" % (ok_or_changed, host, item)

        append_to_log(msg)

    def runner_on_skipped(self, host, item=None):
        if item:
            msg = "skipping: [%s] => (item=%s)" % (host, item)
        else:
            msg = "skipping: [%s]" % host

        append_to_log(msg)

    def runner_on_unreachable(self, host, res):
        item = None

        if type(res) == dict:
            item = res.get('item', None)
            if isinstance(item, str):
                item = utils.str.to_bytes(item)
            results = basic.json_dict_unicode_to_bytes(res)
        else:
            results = utils.str.to_bytes(res)
        host = utils.str.to_bytes(host)
        if item:
            msg = "fatal: [%s] => (item=%s) => %s" % (host, item, results)
        else:
            msg = "fatal: [%s] => %s" % (host, results)

        append_to_log(msg)

    def runner_on_no_hosts(self):
        append_to_log("FATAL: no hosts matched or all hosts have already failed -- aborting")
        pass

    def playbook_on_task_start(self, name, is_conditional):
        name = utils.str.to_bytes(name)
        msg = "TASK: [%s]" % name
        if is_conditional:
            msg = "NOTIFIED: [%s]" % name


        append_to_log(banner(msg))

    def playbook_on_setup(self):
        append_to_log(banner('GATHERING FACTS'))
        pass

    def playbook_on_play_start(self, name):
        append_to_log(banner("PLAY [%s]" % name))
        pass

    def playbook_on_stats(self, stats):
        """Complete: Flush log to database"""
        has_errors = False
        hosts = list(stats.processed.keys())

        for h in hosts:
            t = stats.summarize(h)

            if t['failures'] > 0 or t['unreachable'] > 0:
                has_errors = True

            msg = "Host: %s, ok: %d, failures: %d, unreachable: %d, changed: %d, skipped: %d" % (h, t['ok'], t['failures'], t['unreachable'], t['changed'], t['skipped'])
            append_to_log(msg)

        flush_to_database(has_errors, stats, self.playbook)