#import argpiarse
import os
from datetime import datetime
import cv2
import numpy as np
import time
#import boto3
import argparse
# coding=utf-8
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication

from upload_data import upload_file

parser = argparse.ArgumentParser()
parser.add_argument('IN_FOLDER')
parser.add_argument('OUT_FOLDER')
parser.add_argument('SAVE_TO_AWS')
args = parser.parse_args()
print(args)

IN_FOLDER = args.IN_FOLDER
OUT_FOLDER = args.OUT_FOLDER
SAVE_TO_AWS = args.SAVE_TO_AWS

sender = '**********'  # 发件人的地址
password = '************'  # 此处是我们刚刚在邮箱中获取的授权码
receivers = '*******l@gmail.com,15******@163.com,1*21158179@qq.com'

if os.path.exists(OUT_FOLDER):
    print("The output folder %s already exists.\n" % OUT_FOLDER)
else:
    os.mkdir(OUT_FOLDER)
    print("Createing output folder %s.\n" % OUT_FOLDER)

def write_video(IN_FOLDER, frames, video_file):
    path = os.path.join(IN_FOLDER,frames[0])
    img = cv2.imread(path)
    print(path)
    height, width, layers = img.shape
    img_size = (width,height)

    out = cv2.VideoWriter(video_file, cv2.VideoWriter_fourcc(*'DIVX'), 15, img_size)
    for frame in frames:
        img = cv2.imread(IN_FOLDER + frame)
        out.write(img)
    out.release()

#s3_client = boto3.client('s3')
#metadata = {
 #   "sender": "junxing.liang@realtimes.cn",
  #  "receiver": "junxing.liang@realtimes.cn"
#}

reset = True

while True:

    if reset:
        all_files = []
        start = datetime.now()
        reset = False
        new_scene = True

    files = os.listdir(IN_FOLDER)
    new_files = list(set(files) - set(all_files))
    

    #print('files :    ', files)
    #print('new files: ', new_files)

    # check if we have new files or not
    if new_files:     
        print("adding files")
        all_files.extend(new_files)
        #print(all_files)
        #print('all files: ', all_files)
        time.sleep(0.1)     

        if new_scene:
            image_input_file = IN_FOLDER + all_files[int(len(files)/2)]
            image = cv2.imread(image_input_file)
            image_ouput_file = OUT_FOLDER + start.strftime("%Y-%m-%d_%H-%M-%S") + '_image.jpg'
            cv2.imwrite(image_ouput_file, image)
            new_scene = False

            #TODO: write image_ouput_file to S3
            if SAVE_TO_AWS.lower() == 'true':
                print('Uploading image...')            
                #upload_file(s3_client, image_ouput_file, metadata=metadata
                # 配置邮箱信息
            
            #sender = '1910884164@qq.com'  # 发件人的地址
            #password = 'clbkcxqbwoqqbfji'  # 此处是我们刚刚在邮箱中获取的授权码
            #receivers = 'junxing.liang@realtimes.cn';'lidong.liang@realtimes.cn'
                #receivers = 'lidong.zhang@realtimes.cn'  # 邮件接受方邮箱地址，可以配置多个，实现群发，注意这里要是字符串
            
            content = MIMEText("<html><h2>...智能家居安防...</h2>", _subtype="html", _charset="utf-8")
            msg = MIMEMultipart('related')
            msg.attach(content)


            imageApart = MIMEImage(open(image_ouput_file, 'rb').read(), image_ouput_file.split('.')[-1])
            imageApart.add_header('Content-Disposition', 'attachment', filename=image_ouput_file)
            msg.attach(imageApart)

            # 邮件标题设置
            msg['Subject'] = '老板来客人了，击毙！'

            # 发件人信息
            msg['From'] = sender

            # 收件人信息
            msg['To'] = receivers

            # 通过授权码,登录邮箱,并发送邮件
            try:
                    server = smtplib.SMTP('smtp.qq.com')  # 配置QQ邮箱的smtp服务器地址
                    server.login(sender, password)
                    server.sendmail(msg['From'], msg['To'].split(','), msg.as_string())
                    print('发送成功')
                    server.quit()

            except smtplib.SMTPException as e:
                    print('error', e)
            

    else:
        #print('no new files')
        time.sleep(0.1)

        # if we have no new files and it's been longer than 3 seconds
        if ((datetime.now() - start).total_seconds() > 6): # if less than 3 seconds have passed and we have new files
            if all_files:
                video_output_file = OUT_FOLDER + start.strftime("%Y-%m-%d_%H-%M-%S") + '_video.avi'
                write_video(IN_FOLDER, all_files, video_output_file)

                # TODO: write video_output_file to S3
                if SAVE_TO_AWS.lower() == 'true':
                    print('Uploading video...')
                    #upload_file(s3_client, video_output_file, metadata=metadata)
                    content = MIMEText("<html><h2>...智能家居安防...</h2>", _subtype="html", _charset="utf-8")
                    msg = MIMEMultipart('related')
                    msg.attach(content)


                    imageApart = MIMEImage(open(video_output_file, 'rb').read(), image_ouput_file.split('.')[-1])
                    imageApart.add_header('Content-Disposition', 'attachment', filename=video_output_file)
                    msg.attach(imageApart)

                # 邮件标题设置
                msg['Subject'] = '老板来客人了，击毙！'

                # 发件人信息
                msg['From'] = sender

                # 收件人信息
                msg['To'] = receivers

                # 通过授权码,登录邮箱,并发送邮件
                try:
                    server = smtplib.SMTP('smtp.qq.com')  # 配置QQ邮箱的smtp服务器地址
                    server.login(sender, password)
                    server.sendmail(msg['From'], msg['To'].split(','), msg.as_string())
                    print('发送成功')
                    server.quit()

                except smtplib.SMTPException as e:
                    print('error', e)
       
                    
            # remove all previous images
            print('RESET')
            for file in all_files:
                os.remove(os.path.join(IN_FOLDER,file))
            reset = True






'''
if there are no photos after x seconds
then write a video to s3

'''

'''
if files: # files will be True if list is not empty
    dt = datetime.now()
    files = os.listdir(IN_FOLDER)
    files.sort()
    image_file = IN_FOLDER + files[int(len(files)/2)]
    video_file = OUT_FOLDER + dt.strftime("%Y-%m-%d_%H-%M-%S") + '_video.avi'
    write_video(video_file, IN_FOLDER, files)
    print(image_file)
    print(video_file)
'''
