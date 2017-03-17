#!/usr/bin/python
#-*- coding:utf-8 -*-

# *****************************************************************************
# 版本更新记录：
# -----------------------------------------------------------------------------
#
# 版本 1.0.0 ， 最后更新于 2016-09-29， by guan.huang
#
# *****************************************************************************
# =============================================================================
# 导入外部模块
# =============================================================================
import os
import ftplib
import paramiko



def Usage():
    print '''                                         
            local_dir : 需上传的本地目录
            upload_dir: 上传到的服务器目录
            filenames:可以是单文件名，type 为字符串；也可以是文件名的集合，type 为 list
            config : ftp 或者 sftp 信息，type 为 dict,keys 信息如下
            config = {'ip':XXX,'port':XXX,'user':XXX,'password':XXX,'uploadtype':ftp}
            config = {'ip':XXX,'port':XXX,'user':XXX,'password':XXX,'uploadtype':sftp}
            用法：
            import upload
            upload.upload(config,upload_dir,local_dir,filenames)
          '''

if __name__ == '__main__':
    Usage()

# ==============================================================================
# 上传函数
# ==============================================================================  
class FileUpload(object):

    def __init__(self,config):    
        self._config = config
        self._ret = True
        self.checkinit()
        
    def checkinit(self):
        if type(self._config) != dict:
            print '服务器字典信息错误'
            self._ret = False
            Usage()            
        for i in ['ip','port','user','password','uploadtype']:
            if i not in self._ftp_config.keys():
                self._ret = False
                Usage()
                print '服务器字典信息错误'
        if self._ftp_config['uploadtype'] != 'ftp' or self._ftp_config['uploadtype'] != 'sftp':
             self._ret = False
             Usage()
             print '上传类型信息错误'

    def connect_ftp(self):
        self._ftp = ftplib.FTP(timeout=60)
        self._ftp.connect(self._config['ip'], self._config['port'])
        self._ftp.set_pasv(True)
        self._ftp.login(self._config['user'], self._config['password'])
       
        return self._ftp
        
    def connect_sftp(self):
        self._sftp = paramiko.Transport((self._config['ip'], self._config['port']))
        self._sftp.connect(username=self._config['user'], password=self._config['password'])
        
        self._sftp_client = paramiko.SFTPClient.from_transport(self._sftp)
        self._sftp_channel = self._sftp_client.get_channel()
        self._sftp_channel.settimeout(10)

        return self._sftp_client    
    
    def ftp_uploadfile(self,upload_dir,local_dir,filenames):
        if self._ret:
            return False
        try:
            self.connect_ftp()
        except Exception,e:
            print e,'ftp无法连接'
            return False
        try:
            self._ftp.cwd(upload_dir)
        except Exception,e:
             print e,'注意没权限进入上报目录'
             pass
        try:
            for filename in filenames:
                file_handler = open(local_dir + filename, 'rb')
                self._ftp.storbinary('STOR .in.' + filename, file_handler, 1024) # 上传文件
                file_handler.close() 
                remote_file_size = self._ftp.size('.in.' + filename)
                if remote_file_size == os.path.getsize(local_dir+filename): #判断本地文件与上传文件大小，相等则上传成功                     
                    self._ftp.rename('.in.' + filename, filename)
                    print 'Remote file %s successful' % filename
                else:
                    try:
                        self._ftp.delete('.in.' + filename)
                    except:
                        pass
                    print 'Remote file %s failed' % filename

            self._ftp.quit()
            return True
        except Exception,e:
            print e,'ftp上传失败'
            self._ftp.quit()
            return False
        
    def sftp_uploadfile(self,upload_dir,local_dir,filenames):
        if self._ret:
            return False
        try:
            self.connect_sftp()
        except Exception,e:
            print e,'sftp无法连接'
            return False  
        try:
            for filename in filenames:
                local_path = local_dir + filename
                upload_temppath = upload_dir + '.in.' + filename
                upload_path = upload_dir + filename

                self._sftp_client.put(local_path, upload_temppath)    
                remote_filesize = self._sftp_client.stat(upload_temppath).st_size
                local_filesize = os.path.getsize(local_path)   
                                                           
                if remote_filesize == local_filesize: 
                    self._sftp_client.rename(upload_temppath, upload_path)
                    print 'Remote file %s successful' % filename
                else:
                    try:
                        self._sftp_client.remove(upload_temppath)
                    except:
                        pass
                    print 'Remote file %s failed' % filename

            self._sftp_client.close()
            self._sftp.close()
            return True
        except Exception,e:
            print e,'sftp上传失败'
            self._sftp_client.close()
            self._sftp.close()
            return False

            
                           
def upload(config,upload_dir,local_dir,filenames):
    
    fileupload = FileUpload(config)
    
    if type(filenames) != list:
        filenames = [filenames]

    if config['uploadtype'] == 'ftp':
        ret = fileupload.ftp_uploadfile(upload_dir,local_dir,filenames)
    elif config['uploadtype'] == 'sftp':
        ret = fileupload.sftp_uploadfile(upload_dir,local_dir,filenames)
        
    return ret
                 

















