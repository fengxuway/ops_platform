$(function(){
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
                    return data + '<input type="hidden" name="server" value="'+row.id+'">';
                }
            },
            { "data" : "InnerIpAddress" },
            { "data" : "PublicIpAddress" },
            { "data" : "RegionName" },
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



    //var allowExtention = ".jpg,.bmp,.gif,.png,.docx,.xlsx,.pptx,.zip,.rar,.txt,.pdf,.sh,.csv,.sql,.zip,.tar.gz";

    //var $uploadFile = $("#uploadFile");
    //
//$uploadFile.html5_upload({
    //    url: url_file_upload,
    //    fieldName: 'uploadFile',
    //    headers:{"X-CSRFToken": $.cookie("csrftoken")},
    //    sendBoundary: window.FormData || $.browser.mozilla,
    //    onStart: function(event, total) {
    //        console.log("on start!");
    //        console.log(event)
    //        console.log(total);
    //        console.log(this);
    //        if($("#file_list").find("tbody").find("tr").size() >= 3){
    //            alert("最多能选择3个文件！");
    //            return false;
    //        }
    //        var extention = this.value.substring(this.value.lastIndexOf(".") + 1).toLowerCase();
    //        if (allowExtention.indexOf(extention) > -1) {
    //            var flag = parseInt($uploadFile.attr('data-flag')) + 1;
    //            $uploadFile.attr("data-flag", flag);
    //
    //            var tr = '<tr id="file_flag_' + flag + '"><td>' + $(this)[0].files[0].name
    //                    + '</td><td class="progress_bar"><span>正在上传</span><div class="upload_progress"></div></td><td><button type="button" class="btn btn-default delete_file">删除</button></td></tr>';
    //            $("#file_list").find("tbody").append(tr);
    //            return true;
    //        }else{
    //            alert("仅支持" + allowExtention + "为后缀名的文件!");
    //            return false;
    //        }
    //    },
    //    onProgress: function(event, progress, name, number, total) {
    //        console.log(progress, number);
    //    },
    //    setName: function(text) {
    //        console.log('setname: ' +text)
    //    },
    //    setStatus: function(text) {
    //        console.log('setStatus: ' +text)
    //    },
    //    setProgress: function(val) {
    //        var $tr = $("#file_flag_" + $uploadFile.attr("data-flag"));
    //        $tr.find("td:eq(1)").find("div.upload_progress").css("width", (val*100) + '%');
    //    },
    //    onFinishOne: function(event, response, name, number, total) {
    //        console.log('onFinishOne: ' );
    //        console.log(event);
    //        console.log(response);
    //        console.log(name);
    //        console.log(number);
    //        console.log(total);
    //        var data = $.parseJSON(response);
    //        if(data.result == true){
    //            var $tr = $("#file_flag_" + $uploadFile.attr("data-flag"));
    //            $tr.find("td:eq(0)").append('<input type="hidden" name="file_path" value="'+data.path+'" form="file_form">');
    //            $tr.find("td:eq(1)").find("div.upload_progress").css("width", '100%');
    //            $tr.find("td:eq(1)").find("span").html("上传完成");
    //        }else{
    //            alert("文件上传失败！" + data.mesage);
    //        }
    //    },
    //    onError: function(event, name, error) {
    //        var $tr = $("#file_flag_" + $uploadFile.attr("data-flag"));
    //        $tr.find("td:eq(1)").find("span").html("上传失败");
    //        console.log(error)
    //    }
    //});

    var $selected_server_list = $("#selected_server_list");
    var $myModal = $("#myModal");
    var $result_table = $("#result_table");

    var $file_list = $("#file_list");
    $file_list.delegate(".delete_file", 'click', function(){
        $(this).parents("tr").remove();
    });
    $(".id_server").click(function(){
        $myModal.find("input:checkbox:checked").prop("checked" , false);
        $myModal.modal("show");
    });

    var $selected_server_table = $("#selected_server_table");
    $("#add_server_btn").click(function(){

        if($server_table.children("tbody").find("tr.selected").size() > 0) {
            var old_selected_id = [];
            $selected_server_table.find("input[name='server_ids']").each(function(i, v){
                old_selected_id.push($(this).val());
            });

            var table = '';
            $server_table.children("tbody").find("tr.selected").each(function (i, v) {
                var $tr = $(this);
                var id = $tr.children("td:eq(1)").children("input[type='hidden']").val()
                if(old_selected_id.indexOf(id) < 0){
                    table += '<tr><td>' + $tr.children("td:eq(1)").html() + '</td>';
                    table += '<td>' + $tr.children("td:eq(2)").html() + '</td>';
                    table += '<td>' + $tr.children("td:eq(3)").html() + '</td>';
                    table += '<td><button type="button" class="btn btn-default delete_file">删除</button></td>;'
                    table += '<td><span class="id_check_status">校验中,请稍等。。。</span></td>;'+
                        '</tr>';
                }
            });
            $("#selected_server_table").find("tbody").append(table);
        }
        $("#myModal").modal("hide").find("tr.selected").removeClass("selected");
    });
    $selected_server_list.delegate(".delete_file", 'click', function(){
        if($selected_server_list.find(".delete_file").size() == 1){
            $selected_server_list.empty();
        }else{
            $(this).parents("tr").remove();
        }
    });
    var $file_form = $("#file_form");
    var $tips = $("#tips");
    function validate(){
        if($("input[name='name']").val() == ''){
            $tips.html(tips('warning', "请填写任务名称"));
            return false;
        }else if($file_list.find("tbody").find("tr").size() == 0){
            $tips.html(tips('warning', "请先上传要分发的文件"));
            return false;
        }else if($("#id_dest").val() == ''){
            $tips.html(tips('warning', "请填写目标路径"));
            return false;
        }else if($selected_server_list.find("tbody").size == 0 || $selected_server_list.find("tbody").find("tr").size() == 0){
            $tips.html(tips('warning', "请选择要分发的目标主机"));
            return false;
        }
        $tips.empty();
        return true;
    }
    $("#submit").click(function(){
        if(validate()){
            $result_table.html('<div class="panel-heading">正在执行。。。</div>');
            simple_ajax({
                url: url_filetransfer_submit,
                data: $file_form.serialize(),
                success: function(data){
                    console.log(data);
                    var html = '<div class="panel-heading">执行结果</div>';
                    var result = $.parseJSON(data.data.result);
                    $.each(result, function(i, v){
                        html += '<div class="panel-body"><p>'+i+'</p></div> ' +
                                '<table class="table table-bordered">';
                        $.each(v, function(k, c){
                            html += '<tr>'
                              +'    <td>'+k+'</td>'
                              +'    <td>'+(c['result']?"发送成功！":"发送失败：" + c['message'])+'</td>'
                              +'</tr>';
                        });
                        html += "</table>";
                    });
                    $result_table.html(html);

                }
            })
        }
        console.log($file_form.serialize())
    });
})