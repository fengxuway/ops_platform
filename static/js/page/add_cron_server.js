$(function () {
    var $server_table = $("#mytable");
    var server_table = $server_table.DataTable({
        // "bFilter": false,//去掉搜索框
        //"bAutoWidth": true, //自适应宽度
        "sPaginationType": "full_numbers",
        //"sAjaxDataProp" : "aData",
        "bDestroy": true,
        "bProcessing": true,
        "iDisplayLength": 10,
        "sAjaxSource": url_server_list,
        "bServerSide": true,
        "columns": [
            {'data': 'id'},
            {
                "data": "InstanceName",
                "render": function (data, type, row, meta) {
                    return data + '<input type="hidden" name="server" value="' + row.id + '">';
                    //console.log(row)

                }

            },
            {"data": "InnerIpAddress"},
            {"data": "PublicIpAddress"},
            {"data": "connect"},
        ],
        "columnDefs": [
            {
                "searchable": false,
                "orderable": false,
                "targets": 0
                // "visible": false,
            }
        ],
        "order": [[2, 'asc']],

        "oLanguage": {
            "sProcessing": "正在加载中......",
            "sLengthMenu": "每页显示 _MENU_ 条记录",
            "sZeroRecords": "没有数据！",
            "sEmptyTable": "表中无数据存在！",
            "sInfo": "当前显示 _START_ 到 _END_ 条，共 _TOTAL_ 条记录",
            "sInfoEmpty": "显示0到0条记录",
            "sInfoFiltered": "数据表中共为 _MAX_ 条记录",
            //"sSearch" : "搜索",
            "oPaginate": {
                "sFirst": "首页",
                "sPrevious": "上一页",
                "sNext": "下一页",
                "sLast": "末页"
            }
        }
    });

    server_table.on('click', 'tr[role="row"]', function () {
        $(this).toggleClass('selected');
    });
    // 添加序号
    server_table.on('order.dt search.dt', function () {
        server_table.column(0, {search: 'applied', order: 'applied'}).nodes().each(function (cell, i) {
            cell.innerHTML = i + 1;
        });
    }).draw();


    var $selected_server_list = $("#selected_server_list");
    var $myModal = $("#myModal");
    var $result_table = $("#result_table");

    var $file_list = $("#file_list");
    $file_list.delegate(".delete_file", 'click', function () {
        $(this).parents("tr").remove();
    });
    $(".id_server").click(function () {
        $myModal.find("input:checkbox:checked").prop("checked", false);
        $myModal.modal("show");
    });

    var $selected_server_table = $("#selected_server_table");

    // 添加按钮
    $("#add_server_btn").click(function () {
        if ($server_table.children("tbody").find("tr.selected").size() > 0) {
            var old_selected_id = [];
            $selected_server_table.find("input[name='server_ids']").each(function (i, v) {
                old_selected_id.push($(this).val());
            });

            var table = '';
            $server_table.children("tbody").find("tr.selected").each(function (i, v) {
                var $tr = $(this);
                var id = $tr.children("td:eq(1)").children("input[type='hidden']").val()
                var datas = $tr.children("td:eq(4)").html()  // 取出server的连接状态
                if (old_selected_id.indexOf(id) < 0) {
                    table += '<tr><td>' + $tr.children("td:eq(1)").html() + '</td>';
                    table += '<td>' + $tr.children("td:eq(2)").html() + '</td>';
                    table += '<td>' + $tr.children("td:eq(3)").html() + '</td>';
                    table += '<td><button type="button" class="btn btn-default delete_file">删除</button></td>;'
                    if (datas > 0) {  // 如果服务的连接状态大于零，说明可连接，页面显示“可连接”
                        table += '<td>' + '可连接' + '</td>;' + '</tr>';
                    }
                    else {   // 如果服务的连接状态小于等于零，说明不可连接，页面显示“不可连接”
                        table += '<td>' + '不可连接' + '</td>;' + '</tr>';
                    }
                }
            });
            // 将拼接出来的内容，追加到页面的#selected_server_table中
            $("#selected_server_table").find("tbody").append(table);
        }
        $("#myModal").modal("hide").find("tr.selected").removeClass("selected");
    });

    //删除按钮
    $selected_server_list.delegate(".delete_file", 'click', function () {
        if ($selected_server_list.find(".delete_file").size() == 1) {
            $selected_server_list.empty();
        } else {
            $(this).parents("tr").remove();
        }
    });

    // 保存定时作业按钮，根据页面状态值进行判断，如果含有“不可连接”字样的内容，则弹出警告框警框
    // 同时添加输入的脚本内容验证功能，如果含有“rm -rf /”,则弹框警告提示
    $("#submit-btn").click(function () {
        console.log(CodeMirrorEditor.getValue())
        //test方法,测试字符串,符合模式时返回true,否则返回false
        var re = /rm -rf \/$/;  //匹配"rm -rf /"命令
        //alert(re.test(str));//true
        if (re.test(CodeMirrorEditor.getValue())) {
            alert('您输入的命令含有"rm -rf /"字符，该命令被禁止使用，请务必核对正确再执行!！');
        }
        else {
            var flag = true;
            $.each($('#selected_server_table').children().next().children(), function (i, items) {
                var contents = $(this).children().last().html();
                if (contents.indexOf("不可连接") >= 0) {
                    flag = false;
                    return false;
                }
            });
            if (flag) {
                $("#operating_form").submit();
            } else {
                alert('请查看当前server状态，确认可连接后，才可保存计划任务!！');
            }
        }
    })
})

