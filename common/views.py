# coding:utf-8
from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse
import os
import logging
from common.forms import PageData
from django.http import HttpResponse, JsonResponse
import traceback


log = logging.getLogger('django')


def download(path, file_name='', content_type='application/octet-stream', chunk=1024):

    def file_iterator(file_path, chunk_size=chunk):
        chunks = 0
        try:
            with open(file_path) as f:
                while True:
                    c = f.read(chunk_size)
                    chunks += chunk_size
                    if c:
                        log.info('    downloading...%d' % chunks)
                        yield c
                    else:
                        break
        except IOError as e:
            log.error("    Download file not Found!" + e.message)
            raise e
    log.info("    Download file: %s" % path)
    if not file_name and path.find(os.sep) > 0:
        file_name = path[path.rindex(os.sep) + 1:]
    log.info("    File name: " + file_name)
    response = StreamingHttpResponse(file_iterator(path))
    response['Content-Type'] = content_type
    response['Content-Disposition'] = 'attachment;filename="' + file_name + '"'
    return response


def page_handler(f):
    """
    使用闭包形式处理分页请求，做预处理操作和结束操作，日志打印等。
    视图层函数只需注解该函数，代码中处理简单的搜索功能，并返回QuerySet对象。
    例见service.views.page函数
    :param f: 视图函数，注解注入
    :return: response
    """
    def hander(*args, **kwargs):
        dp = PageData(args[0].GET)
        if dp.is_valid():
            page_info = dp.get_page_info()
            try:
                query = f(*args, **kwargs)
                order = dp.get_sort_rule()
                order_col = order[0]
                if order[1] != 'asc':
                    order_col = "-" + order[0]

                data_q = query.order_by(order_col)[page_info[0]:page_info[0] + page_info[1]]
                data = [x.to_dict() for x in data_q]
                length = query.count()
                mp = dp.get_data(data, length)
                return JsonResponse(mp)
            except Exception:
                log.error('search got ERROR: ' + traceback.format_exc())
                return JsonResponse({'result': False, 'message': 'search get the ERROR: \n' + traceback.format_exc()})
        return JsonResponse({'result': False, 'message': 'the Request params probably lose something.'})
    return hander


def handle_uploaded_file(path, upload_file):
    """
    上传文件保存到指定路径下。返回保存后文件的全路径
    :param path: 要保存的路径
    :param upload_file: InMemoryUploadedFile 对象
    :return: 文件全路径
    """
    file_path = os.path.join(path, upload_file.name)
    # 判断文件路径是否存在
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        # 上传文件到指定路径
        with open(file_path, 'wb+') as f:
            for chunk in upload_file.chunks():
                f.write(chunk)
        return file_path
    except Exception as e: # 忽略错误
        log.error('File upload got Error: \n' + traceback.format_exc())
        raise e
