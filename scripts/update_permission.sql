UPDATE `ntdeploy`.`auth_permission` SET `name`='访问镜像' WHERE `codename`='view_image';
UPDATE `ntdeploy`.`auth_permission` SET `name`='访问服务器' WHERE `codename`='view_server';
UPDATE `ntdeploy`.`auth_permission` SET `name`='访问域名映射' WHERE `codename`='view_domain';
UPDATE `ntdeploy`.`auth_permission` SET `name`='访问服务' WHERE `codename`='view_service';
UPDATE `ntdeploy`.`auth_permission` SET `name`='访问数据字典' WHERE `codename`='view_dataoption';
UPDATE `ntdeploy`.`auth_permission` SET `name`='添加GRID版本' WHERE `codename`='add_gridversion';
UPDATE `ntdeploy`.`auth_permission` SET `name`='修改GRID版本' WHERE `codename`='change_gridversion';
UPDATE `ntdeploy`.`auth_permission` SET `name`='删除GRID版本' WHERE `codename`='delete_gridversion';
UPDATE `ntdeploy`.`auth_permission` SET `name`='添加GRID版本信息' WHERE `codename`='add_versioninfo';
UPDATE `ntdeploy`.`auth_permission` SET `name`='修改GRID版本信息' WHERE `codename`='change_versioninfo';
UPDATE `ntdeploy`.`auth_permission` SET `name`='删除GRID版本信息' WHERE `codename`='delete_versioninfo';
UPDATE `ntdeploy`.`auth_permission` SET `name`='添加GRID' WHERE `codename`='add_grid';
UPDATE `ntdeploy`.`auth_permission` SET `name`='修改GRID' WHERE `codename`='change_grid';
UPDATE `ntdeploy`.`auth_permission` SET `name`='删除GRID' WHERE `codename`='delete_grid';
UPDATE `ntdeploy`.`auth_permission` SET `name`='添加镜像' WHERE `codename`='add_image';
UPDATE `ntdeploy`.`auth_permission` SET `name`='修改镜像' WHERE `codename`='change_image';
UPDATE `ntdeploy`.`auth_permission` SET `name`='删除镜像' WHERE `codename`='delete_image';
UPDATE `ntdeploy`.`auth_permission` SET `name`='添加服务器' WHERE `codename`='add_server';
UPDATE `ntdeploy`.`auth_permission` SET `name`='修改服务器' WHERE `codename`='change_server';
UPDATE `ntdeploy`.`auth_permission` SET `name`='删除服务器' WHERE `codename`='delete_server';
UPDATE `ntdeploy`.`auth_permission` SET `name`='添加域名映射' WHERE `codename`='add_domain';
UPDATE `ntdeploy`.`auth_permission` SET `name`='修改域名映射' WHERE `codename`='change_domain';
UPDATE `ntdeploy`.`auth_permission` SET `name`='删除域名映射' WHERE `codename`='delete_domain';
UPDATE `ntdeploy`.`auth_permission` SET `name`='添加服务' WHERE `codename`='add_service';
UPDATE `ntdeploy`.`auth_permission` SET `name`='修改服务' WHERE `codename`='change_service';
UPDATE `ntdeploy`.`auth_permission` SET `name`='删除服务' WHERE `codename`='delete_service';
UPDATE `ntdeploy`.`auth_permission` SET `name`='添加数据字典' WHERE `codename`='add_dataoption';
UPDATE `ntdeploy`.`auth_permission` SET `name`='修改数据字典' WHERE `codename`='change_dataoption';
UPDATE `ntdeploy`.`auth_permission` SET `name`='删除数据字典' WHERE `codename`='delete_dataoption';
UPDATE `ntdeploy`.`auth_permission` SET `name`='添加脚本执行' WHERE `codename`='add_runscript';
UPDATE `ntdeploy`.`auth_permission` SET `name`='修改脚本执行' WHERE `codename`='change_runscript';
UPDATE `ntdeploy`.`auth_permission` SET `name`='删除脚本执行' WHERE `codename`='delete_runscript';
UPDATE `ntdeploy`.`auth_permission` SET `name`='添加文件分发' WHERE `codename`='add_filetransfer';
UPDATE `ntdeploy`.`auth_permission` SET `name`='修改文件分发' WHERE `codename`='change_filetransfer';
UPDATE `ntdeploy`.`auth_permission` SET `name`='删除文件分发' WHERE `codename`='delete_filetransfer';
UPDATE `ntdeploy`.`auth_permission` SET `name`='添加作业' WHERE `codename`='add_job';
UPDATE `ntdeploy`.`auth_permission` SET `name`='修改作业' WHERE `codename`='change_job';
UPDATE `ntdeploy`.`auth_permission` SET `name`='删除作业' WHERE `codename`='delete_job';
UPDATE `ntdeploy`.`auth_permission` SET `name`='添加计划任务' WHERE `codename`='add_cronjob';
UPDATE `ntdeploy`.`auth_permission` SET `name`='修改计划任务' WHERE `codename`='change_cronjob';
UPDATE `ntdeploy`.`auth_permission` SET `name`='删除计划任务' WHERE `codename`='delete_cronjob';
DELETE FROM `ntdeploy`.`auth_permission` WHERE `codename`='add_taskrecord';
DELETE FROM `ntdeploy`.`auth_permission` WHERE `codename`='change_taskrecord';
DELETE FROM `ntdeploy`.`auth_permission` WHERE `codename`='delete_taskrecord';