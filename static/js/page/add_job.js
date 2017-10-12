/**
 * Created by fengxu on 16-6-22.
 */
function heredoc(fn) {
    return fn.toString().split('\n').slice(1,-1).join('\n') + '\n'
}
var is_total_server = true;
var filetransfer_html = heredoc(function(){/*
                                <li><i class="fa king-bg-blue">__panel_num__</i>
                                    <div class="panel panel-info" data-id="__id__" id="task___id__">
                                        <input type="hidden" name="type___id__" value="file">
                                        <input type="hidden" name="id_order" value="__id__">
                                        <div class="panel-heading">
                                            <h3 class="panel-title"><strong>文件</strong>&nbsp;步骤名称：<input class="form-control" type="text" name="title___id__" required>
                                            <a style="float: right;" href="javascript:void(0);" class="remove_task btn btn-default"><i class="fa fa-close"></i></a>
                                            <a style="float: right; margin-right:10px;" href="javascript:void(0);" class="scroll_task btn btn-default"><i class="fa fa-chevron-down"></i></a>
                                            </h3>
                                            <span class="server_ids"></span>
                                            <div style="clear:both;"></div>
                                        </div>
                                        <table class="table table-bordered">
                                            <thead>
                                            <tr>
                                                <th>执行账户</th>
                                                <th>服务器数</th>
                                                <th>目标路径</th>
                                            </tr>
                                            </thead>
                                            <tbody>
                                            <tr>
                                                <td><input class="form-control" type="text" name="user___id__" value="root" readonly></td>
                                                <td><input class="form-control" type="text" name="server_count___id__" value="0" readonly></td>
                                                <td><input class="form-control" type="text" name="path___id__" required></td>
                                            </tr>
                                            </tbody>
                                        </table>
                                        <div class="panel-body" style="display:none;">
                                            <div class="form-group">
                                                <label class="col-sm-2 control-label">选择文件</label>
                                                <div class="col-sm-10">
                                                    <div class="file-box">
                                                        <button type="button" class="btn btn-primary textfield"><i class="fa fa-upload" aria-hidden="true"></i>&nbsp;上传文件</button>
                                                        <input type="file" name="uploadFile" class="uploadFile file input_file" size="28" />
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="form-group">
                                                <label class="col-sm-2 control-label">文件列表</label>
                                                <div class="col-sm-10">
                                                    <table class="file_list table table-bordered">
                                                        <thead>
                                                        <tr>
                                                            <th>文件名</th>
                                                            <th>上传状态</th>
                                                            <th>操作</th>
                                                        </tr>
                                                        </thead>
                                                        <tbody>
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </div>
                                            <div class="form-group dest_server_form">
                                                <label class="col-sm-2 control-label">目标主机</label>
                                                <div class="col-sm-10">
                                                    <button type="button" class="select_server btn btn-primary">选择服务器</button>
                                                </div>
                                            </div>
                                            <div class="form-group dest_server_form">
                                                <label class="col-sm-2 control-label"></label>
                                                <div class="col-sm-10">
                                                    <div class="selected_server_list">
                                                        <table class="selected_server_table table table-bordered table-hover">
                                                            <thead>
                                                            <tr>
                                                                <th>主机名</th>
                                                                <th>内网IP</th>
                                                                <th>外网IP</th>
                                                                <th>操作</th>
                                                            </tr>
                                                            </thead><tbody></tbody>
                                                        </table>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div></li>
*/});
var runscript_html = heredoc(function(){/*
                                <li><i class="fa king-bg-blue">__panel_num__</i>
                                    <div class="panel panel-success" data-id="__id__" id="task___id__">
                                        <input type="hidden" name="type___id__" value="script">
                                        <input type="hidden" name="id_order" value="__id__">
                                        <div class="panel-heading">
                                            <h3 class="panel-title"><strong>脚本</strong>&nbsp;步骤名称：<input class="form-control" type="text" name="title___id__" required>
                                            <a style="float: right;" href="javascript:void(0);" class="remove_task btn btn-default"><i class="fa fa-close"></i></a>
                                            <a style="float: right; margin-right:10px;" href="javascript:void(0);" class="scroll_task btn btn-default"><i class="fa fa-chevron-down"></i></a>
                                            </h3>
                                            <span class="server_ids"></span>

                                            <div style="clear:both;"></div>
                                        </div>
                                        <table class="table table-bordered">
                                            <thead>
                                            <tr>
                                                <th>执行账户</th>
                                                <th>服务器数</th>
                                                <th>脚本参数</th>
                                            </tr>
                                            </thead>
                                            <tbody>
                                            <tr>
                                                <td><input class="form-control" type="text" name="user___id__" value="root" readonly></td>
                                                <td><input class="form-control" type="text" name="server_count___id__" value="0" readonly></td>
                                                <td><input class="form-control" type="text" name="args___id__"></td>
                                            </tr>
                                            </tbody>
                                        </table>
                                        <div class="panel-body" style="display:none;">
                                            <div class="form-group">
                                                <label for="id_script_source" class="col-sm-2 control-label">脚本来源</label>

                                                <div class="col-sm-7">
                                                    <label class="raido-inline">
                                                        <input type="radio" value="1" name="radioform" checked="checked">手工录入</label>&nbsp;&nbsp;
                                                    <label class="raido-inline">
                                                        <input type="radio" value="2" name="radioform">本地脚本</label>
                                                </div>
                                            </div>
                                            <div class="form-group" style="display : none;">
                                                <label class="col-sm-2 control-label"></label>
                                                <div class="col-sm-7">
                                                    <div class="well well-lg">
                                                        <div class="btn btn-primary">
                                                            <input name="local_file" type="file" class="upload"/>
                                                        </div>
                                                        目前支持 .sh 后缀脚本
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="form-group">
                                                <label class="col-sm-2 control-label">脚本内容</label>
                                                <div class="col-sm-10">
                                                    <textarea class="shell_editor" name="script_content___id__">#!/bin/bash
</textarea>
                                                </div>
                                            </div>
                                            <div class="form-group dest_server_form">
                                                <label class="col-sm-2 control-label">目标主机</label>
                                                <div class="col-sm-10">
                                                    <button type="button" class="select_server btn btn-primary">选择服务器</button>
                                                </div>
                                            </div>
                                            <div class="form-group dest_server_form">
                                                <label class="col-sm-2 control-label"></label>
                                                <div class="col-sm-10">
                                                    <div class="selected_server_list">
                                                        <table class="selected_server_table table table-bordered table-hover">
                                                            <thead>
                                                            <tr>
                                                                <th>主机名</th>
                                                                <th>内网IP</th>
                                                                <th>外网IP</th>
                                                                <th>操作</th>
                                                            </tr>
                                                            </thead><tbody></tbody>
                                                        </table>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div></li>
*/});


$(function(){
    // upload_file_count 上传文件记录数，放在每个上传文件后增加的tr中作为ID，方便进度条等功能定位到当前文件关联行中。
    var upload_file_count = 0;
    var task_sequence = 1;
    var editors = new Map();
    var $tips = $("#tips");
    // 每个子任务的server选择列表，用于显示和隐藏
    function display_dest_server(){
        if(is_total_server){
            $(".dest_server_form").hide();
        }else{
            $(".dest_server_form").show();
        }
    }


    var $server_table = $("#server_table");
    var server_table = $server_table.DataTable({
        // "bFilter": false,//去掉搜索框
        //"bAutoWidth": true, //自适应宽度
        "sPaginationType" : "full_numbers",
        //"sAjaxDataProp" : "aData",
        "bDestroy" : true,
        "bProcessing" : true,
        "iDisplayLength": 10,
        "sAjaxSource" : url_server_list,
        "bServerSide" : true,
        "columns" : [
            { 'data': 'id'},
            { "data" : "InstanceName",
                "render": function(data, type, row, meta) {
                    return data + '<input type="hidden" name="server_ids" value="'+row.id+'">';
                }
            },
            { "data" : "InnerIpAddress" },
            { "data" : "PublicIpAddress" },
            { "data" : "Cpu",
                "render": function (data, type, row, meta) {
                    var cpu = data;
                    var tmp = (row.Memory / 1024.0).toFixed(1);
                    var memory = (parseInt(tmp) == tmp ? parseInt(tmp) : tmp);
                    var type_flag = '';
                    var title_flag = '';
                    if(row.DiskType == 'SSD' || row.DiskType == 'EFFICIENCY'){
                        type_flag = row.DiskType[0];
                        title_flag = 'SSD';
                        if(row.DiskType == 'EFFICIENCY'){
                            title_flag = '混合硬盘';
                        }
                    }
                    var disk = row.DiskSize + type_flag;
                    var title = 'CPU核心数: ' + cpu + '\n内存: ' + memory
                            + ' GB\n硬盘: ' + row.DiskSize + ' GB' + (title_flag ? "(" + title_flag + ")":"");
                    return '<span title="' + title + '">' + cpu + ' / ' + memory + ' / ' + disk + '</span>';
                }
            }
        ],
        "columnDefs": [
            {
                "searchable": false,
                "orderable": false,
                "targets":0
                 // "visible": false,
            }
        ],
        "order": [[ 2, 'asc' ]],

        "oLanguage" : {
            "sProcessing" : "正在加载中......",
            "sLengthMenu" : "每页显示 _MENU_ 条记录",
            "sZeroRecords" : "没有数据！",
            "sEmptyTable" : "表中无数据存在！",
            "sInfo" : "当前显示 _START_ 到 _END_ 条，共 _TOTAL_ 条记录",
            "sInfoEmpty" : "显示0到0条记录",
            "sInfoFiltered" : "数据表中共为 _MAX_ 条记录",
            //"sSearch" : "搜索",
            "oPaginate" : {
                "sFirst" : "首页",
                "sPrevious" : "上一页",
                "sNext" : "下一页",
                "sLast" : "末页"
            }
        }
    });

    server_table.on('click', 'tr[role="row"]', function(){
        $(this).toggleClass('selected');
    });
    // 添加序号
    server_table.on('order.dt search.dt', function(){
        server_table.column(0, {search:'applied', order:'applied'}).nodes().each(function(cell, i) {
            cell.innerHTML = i+1;
        });
    }).draw();


    $(".box-header").delegate("input[name='local_file']", 'change', function(){
        var $this = $(this);
        //支持chrome IE10
        if (window.FileReader) {
            var file = this.files[0];
            var reader = new FileReader();
            reader.onload = function () {
                console.log(this.result);
                var tmp_txt = $this.parents("div.form-group").next("div.form-group").find("textarea");
                editors[tmp_txt.attr("name")].setValue(this.result);
            };
            reader.readAsText(file);
        }
    });

    //单选按钮隐藏/显示div
    $(":radio[name='radioform']").click(function () {
        var index = $(":radio[name='radioform']").index($(this));
        var val = $("input[name='radioform']:checked").val();
        console.log(val)
        if (val == '1') { //选中第2个时，div显示
            $(this).parents(".form-group").next('.form-group').slideUp("fast");
        }
        else {
            $(this).parents(".form-group").next('.form-group').slideDown("fast");
        }

    });

    $("#submit_btn").click(function(){
        console.log($("#form").serialize());
        $("#form").submit();
    });

    var allowExtention = ".jpg,.bmp,.gif,.png,.docx,.xlsx,.pptx,.zip,.rar,.txt,.pdf,.sh,.csv,.sql,.zip,.tar.gz";

    var $uploadFile = $(".uploadFile");
    var ooo = {
        url: url_file_upload,
        fieldName: 'uploadFile',
        headers:{"X-CSRFToken": $.cookie("csrftoken")},
        sendBoundary: window.FormData || $.browser.mozilla,
        onStart: function(event, total) {
            console.log($(this));
            var $tmp_table = $(this).parents("div.form-group").next('.form-group').find('table.file_list');
            if($tmp_table.find("tbody").find("tr").size() >= 3){
                alert("最多能选择3个文件！");
                return false;
            }
            var extention = this.value.substring(this.value.lastIndexOf(".") + 1).toLowerCase();
            if (allowExtention.indexOf(extention) > -1) {
                upload_file_count += 1;
                var tr = '<tr id="file_flag_' + upload_file_count + '"><td>' + $(this)[0].files[0].name
                        + '</td><td class="progress_bar"><span>正在上传</span><div class="upload_progress"></div></td><td><button type="button" class="btn btn-default delete_file">删除</button></td></tr>';
                $tmp_table.find("tbody").append(tr);
                return true;
            }else{
                alert("仅支持" + allowExtention + "为后缀名的文件!");
                return false;
            }
        },
        setProgress: function(val) {
            var $tr = $("#file_flag_" + upload_file_count);
            $tr.find("td:eq(1)").find("div.upload_progress").css("width", (val*100) + '%');
        },
        onFinishOne: function(event, response, name, number, total) {
            var data = $.parseJSON(response);
            if(data.result == true){
                var $tr = $("#file_flag_" + upload_file_count);
                var prefix = $tr.parents("div.panel").attr("data-id");
                $tr.find("td:eq(0)").append('<input type="hidden" name="file_path_'+prefix+'" value="'+data.path+'">');
                $tr.find("td:eq(1)").find("span").html("上传完成");
            }else{
                alert("文件上传失败！" + data.mesage);
            }
        },
        onError: function(event, name, error) {
            var $tr = $("#file_flag_" + upload_file_count);
            $tr.find("td:eq(1)").find("span").html("上传失败");
            console.log(error)
        }
    };
    $uploadFile.html5_upload(ooo);


    $("#add_file_task").click(function(){
        task_sequence ++;
        $(".king-timeline").append(filetransfer_html.replace(/__id__/g, task_sequence).replace(/__panel_num__/g, panel_num++));
        display_dest_server();
        console.log("#task_"+ task_sequence)
        console.log($("#task_"+ task_sequence));
        $("#task_"+ task_sequence).find('.uploadFile').html5_upload(ooo);
    });
    $("#add_script_task").click(function(){
        task_sequence ++;
        $(".king-timeline").append(runscript_html.replace(/__id__/g, task_sequence).replace(/__panel_num__/g, panel_num++));
        display_dest_server();
        var tmp_txt = $("#task_"+ task_sequence).find("textarea");
        editors[tmp_txt.attr("name")] = CodeMirror.fromTextArea(tmp_txt[0], {
            mode: "text/x-sh",  //设置语法高亮
            lineNumbers: true,       //显示行号
            tabSize: 4,             //tab缩进为4
            smartIndent: true,      //是否智能缩进
            matchBrackets: true,
            styleActiveLine: true,
            lineWrapping: true, //是否强制换行
            theme: "abcdef",  //样式
            scrollbarStyle: "native", //
            lineWiseCopyCut: true,  //启用时，如果在复制或剪切时没有选择文本，那么就会自动操作光标所在的整行
            cursorHeight: "0.85"  //光标高度。默认为1，也就是撑满行高。对一些字体，设置0.85看起来会更好。

        });
    });

    function refresh_panel_num(){
        var _panel_num = 1;
        $(".king-timeline").find("i.king-bg-blue").each(function(){
            $(this).html(_panel_num++);
        });
        panel_num = _panel_num;
    }


    var $add_server_btn = $("#add_server_btn");
    var $add_server_btn_new = $("#add_server_btn_new");
    $(".box-header").delegate(".delete_file", 'click', function(){
        $(this).parents("tr").remove();
    }).delegate(".delete_server", 'click', function(){
        var $input = $(this).parents("div.panel").find("input[name^='server_count_']");
        var $tbody = $(this).parents("tbody");
        $(this).parents("tr").remove();
        $input.val($tbody.find("tr").size());
    }).delegate(".select_server", 'click', function(){
        var task_id = $(this).parents("div.panel").attr("id");
        $add_server_btn_new.attr("data-task-id", task_id);
        $newModal.modal("show");
    }).delegate(".remove_task", 'click', function(){
        if(confirm("您确定要删除该任务吗？")){
            $(this).parents("div.panel").parent("li").remove();
            refresh_panel_num();
        }
    }).delegate(".scroll_task", 'click', function(){
        var $panel = $(this).parents(".panel");
        if($(this).children("i").hasClass('fa-chevron-up')){
            $panel.find(".panel-body").slideUp('fast');
            $(this).children("i").removeClass("fa-chevron-up").addClass("fa-chevron-down");
        }else{
            $panel.find(".panel-body").slideDown('fast');
            $(this).children("i").removeClass("fa-chevron-down").addClass("fa-chevron-up");
            var data_id = $panel.attr("data-id");
            if($panel.find("input[name='type_"+data_id+"']").val() == 'script'){
                editors[$panel.find("textarea.shell_editor").attr("name")].refresh();
            }
        }
    });


    var $newModal = $("#newModal");

    $add_server_btn_new.click(function(){
        var task = $(this).attr("data-task-id");
        var task_id = task.replace('task_', '');
        var $task_div = $("#" + task);
        /* var hidden_html = [];
        $server_table.find("tbody").find("tr.selected").each(function(i, v){
            var $tr = $(this);
            var srv_id = $tr.find("input[name='server_ids']").val();
            hidden_html.push('<input type="hidden" name="server_ids_'+task_id+'" value="'+srv_id+'">');
        }); */
        // $task_div.find("span.server_ids").html(hidden_html.join(' '));


        if($server_table.children("tbody").find("tr.selected").size() > 0) {
            var old_selected_id = [];
            var $selected_tbody = $task_div.find(".selected_server_table").find("tbody");
            $selected_tbody.find("input[name='server_ids_"+task_id+"']").each(function(i, v){
                old_selected_id.push($(this).val());
            });

            var table = '';
            $server_table.children("tbody").find("tr.selected").each(function (i, v) {
                var $tr = $(this);
                var id = $tr.children("td:eq(1)").children("input[type='hidden']").val();
                if(old_selected_id.indexOf(id) < 0){
                    table += '<tr><td>' + $tr.children("td:eq(1)").text()
                          + '<input type="hidden" name="server_ids_' + task_id + '" value="'
                          + $tr.children("td:eq(1)").children("input[type='hidden']").val() + '"></td>';
                    table += '<td>' + $tr.children("td:eq(2)").html() + '</td>';
                    table += '<td>' + $tr.children("td:eq(3)").html() + '</td>';
                    table += '<td><button type="button" class="btn btn-default delete_server">删除</button></td></tr>';
                }
            });
            $selected_tbody.append(table);
        }
        $newModal.modal("hide").find("tr.selected").removeClass("selected");
        $("input[name='server_count_"+task_id+"']").val($selected_tbody.find("tr").size());
    });

    var $is_total_server = $("input[name='is_total_server']");

    $("#form").html5Validate(function() {
        // 全部验证通过
        this.submit();
    }, {
        validate: function() {
            if($is_total_server.is(":checked")){
                if($("input[name='server_ids_all']").size() == 0){
                    $is_total_server.parents("div.panel").find("button.select_server").testRemind('请选择目标服务器').focus();
                    return false;
                }
            }else{
                var server_count_flag = true;
                $("input[name^='server_count_']").each(function(i, v){
                    if($(this).val() == '0'){
                        server_count_flag = false;
                        $(this).parents("div.panel").find("button.select_server").testRemind('请选择目标服务器').focus();
                        return false
                    }
                });
                if(!server_count_flag){
                    return false;
                }
            }

            return true;
        },
        labelDrive:true
    });



    $is_total_server.click(function(){
        return false;
        /* if($is_total_server.is(":checked")){
            $is_total_server.parents("div.panel").find("div.panel-body").slideDown('fast');
            is_total_server = true;
            display_dest_server();
        }else{
            $is_total_server.parents("div.panel").find("div.panel-body").slideUp('fast');
            is_total_server = false;
            display_dest_server();
        }
        */
    })

});