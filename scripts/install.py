#/usr/bin/env python
# coding:utf-8

import os,sys
import configparser
import subprocess
import traceback


def read_ini(ini_path):
    try:
        if not os.path.exists(ini_path):
            raise IOError('Ini file not exists.')
        cfg = configparser.ConfigParser()
        cfg.read(ini_path)
        return cfg
    except Exception:
        print("Error.")
        return None


def kill_java():
    command = "pkill java"
    subprocess.getoutput(command)


def install_rpm(rpm_path,cfg=None):
    print("Install RPM Image starting...")
    command = "rpm -Uvh --oldpackage " + rpm_path
    os.system(command)
    if cfg:
        if "nginx_php_memcache" in rpm_path:
            install_command = cfg.get("operation", "install")
            os.system(install_command)
        else:
            print("This rpm is not nginx_php_memcache_env")
    else:
        print("not found cfg")
    print("Install RPM Image complete.")


def sed(file_path, name, value):
    value = value.replace("/", "\/").replace("=", "\=").replace("&", "\&").replace("$", "\$")  # 转意排除
    command = "sed -i 's/||" + name + "||/" + value + "/i' " + file_path + ""  # sed /i 忽略大小写
    subprocess.getoutput(command)


def change_app_config(cfg):
    print("Modify Config files starting...")
    try:
        default_path = cfg.get("install", "default_dir")

        if 'config' in cfg.sections():
            for config_name, config_path in cfg.items('config'):
                if not os.path.isabs(config_path):
                    config_path = os.path.join(default_path, config_path)
                for key, value in cfg.items(config_name):
                    sed(config_path, key, value)
            print("Config files Modefy complete.")
        else:
            print('Ini file not found section named [config].')
    except configparser.NoSectionError as e:
        print("Ini file not found section. " + e.message)
    except configparser.NoOptionError as e:
        print("Ini file not found section. " + e.message)
    except Exception as e:
        print("change config got error: \n")
        traceback.print_exc()
    # if default_path:
    #     s = cfg.sections()
    #     print u"Modify Config files starting..."
    #     for k1 in s:
    #         for k2,v2 in cfg.items(k1):
    #             if k1 == "config":   # 判定是否为修改文件
    #                 for k3,v3 in cfg.items(k2):
    #                     conf_service = cfg.get(k2, k3)
    #                     re_config_service = conf_service.replace("/","\/")
    #                     app_service_full_path=os.path.join(default_path, v2)  # 文件全路径
    #                     command = "sed -i 's/||"+k3+"||/"+re_config_service+"/i' "
    # +app_service_full_path+""  # sed -i 忽略大小写
    #                     commands.getoutput(command)


def service_restart(cfg):
    command = cfg.get("operation", "restart")
    if command:
        print("Restart Service...")
        os.system(command)
        print("Restart Service complete.")
    else:
        print("Restart Service error. Restart command not found.")


def main():
    if len(sys.argv) >= 3:
        cfg = read_ini(sys.argv[2])
        install_rpm(sys.argv[1],cfg)
        if cfg:
            change_app_config(cfg)
        # service_restart(cfg)
    elif len(sys.argv) >= 2:
        install_rpm(sys.argv[1])





if __name__ == "__main__":
    main()
