import streamlit as st
import pandas as pd
import boto3
import string
import random
import fnmatch
import io
import os
import unicodedata
# cloudflare_api_token = 'VxTbMDc1gZJ828Z9TZUsy3_UwpfdMSlYPeexgaTg'
#oFFline 관리용
ACCESS_KEY_ID = '6ee076ab03e448ff6174eb2c36896e58'
SECRET_ACCESS_KEY = 'e6123b2dc68c00cf1f3c9082b3c37f90c1185b974d04d5cee5b268eba1a1cba5'
#Online에서는 반드시 비밀/환경변수 등으로 설정할 것!.



@st.cache_resource
def cloudflare_access():
    s3 = boto3.resource("s3",
        endpoint_url="https://9442d6ca46b34b9227318540e32aa01b.r2.cloudflarestorage.com",
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY)
    return s3
s3 = cloudflare_access()

@st.cache_resource
def cloudflare_access2():
    s3 = boto3.client("s3",
        endpoint_url="https://9442d6ca46b34b9227318540e32aa01b.r2.cloudflarestorage.com",
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY)
    return s3

s3_client = cloudflare_access2()


def url_get(bucketname,filename):
    return f"https://pub-dfbf8bb84484433186b0d6fef056f604.r2.dev/{bucketname}/{filename}"

# def url_get(bucketname,filename):
#     return f"https://9442d6ca46b34b9227318540e32aa01b.r2.cloudflarestorage.com/{bucketname}/{filename}"



def change_state(BUCKET_NAME):
    response = s3_client.put_bucket_settings(
    Bucket=BUCKET_NAME,
    Configuration={
        "MaxKeys": 10000,
    },
)
    return response

#파일 업로드
def upload_cloudflare(bucketname,filename,blobname : str = 'any'):
    
    if blobname == 'any':
        key = filename
    else:
        pass
    res = s3.Object(bucketname, key).put(Body=filename.getvalue())
    # res = s3.Object(bucketname, key).put(Body=open(filename, "rb").read())
    return res


# upload = st.button('upload')
# if upload:
#     res =  upload_cloudflare('testbucket001','/Users/julimpark/Documents/KOREA/파이썬 연습/code_ARCHIVE/streamlit_master/etc.py',)
#     st.write(res)

def upload(filename,bucketname,key):
    # with open(filename,'rb') as data:
        s3_client.upload_fileobj(filename,bucketname,key)
import json
def json_upload(bucketname, filename,filecontents):
    response = s3_client.put_object(
        Bucket=bucketname,
        Key=filename,
        Body=json.dumps(filecontents),
        ContentType="application/json",
    )
    return response

def upload_bytesio(bucketname, filename,filecontents):
    response = s3_client.upload_fileobj(filecontents,bucketname,filename)
    return response

def upload2(filename,bucketname,key):
    # with open(filename,'rb') as data:
        s3_client.put_object(Body=filename,Bucket=bucketname,Key=key)#Bucket=bucket_name, Key=file_name, Body=csv_data.getvalue()
    # s3.upload_file(filename,bucketname,key)

def download2(bucketname,filename):
    data = io.StringIO()
    with open(filename, 'wb') as data:
        s3_client.download_fileobj(bucketname,filename,data)
        # with open(data,'rb') as f:
        #     data_io = io.BytesIO(data)
    return data
    

def get_download_folder_path():
  """
  맥과 윈도우를 구분하지 않고 다운로드 폴더 주소를 자동으로 찾습니다.

  Returns:
    다운로드 폴더 주소.
  """

  if os.name == "nt":
    return os.path.join(os.environ["USERPROFILE"], "Downloads")
  else:
    return os.path.expanduser("~/Downloads")


def download(bucketname,filename):
    with open(filename, 'wb') as data:
        s3_client.download_fileobj(bucketname,filename,data)
        # with open(data,'rb') as f:
        #     data_io = io.BytesIO(data)
    return data

###이것이 바이츠 아이오에 다운로드 받는 방법!!!!!!from Bard
def download3(bucketname,filename):
    response = s3_client.get_object(Bucket=bucketname,Key=filename)
    bytesio = io.BytesIO()
    bytesio.write(response["Body"].read())
    return bytesio.getvalue()

# 파일 다운로드
def download_cloudflare(bucketname,blobname,filename:str='any'):
    # 다운로드할 파일의 키를 지정합니다.
    key = blobname
    downfolder = get_download_folder_path()
    # 다운로드할 파일의 경로를 지정합니다.
    if filename =='any':
        download_file_path = f"{downfolder}/{blobname.split('/')[1]}"
    else:
        download_file_path = filename

    # 파일을 다운로드합니다.
    with open(download_file_path, "wb") as f:
        
        # res = s3.Object(bucketname, key).download_file(f)
        f.write(download3(bucketname,blobname)) #따로 리턴되는 값 없음. 별도 다운로드 폴더 확인
        f.close()


# download = st.button('download')
# if download:
#     res =  download_cloudflare('testbucket001','produict.csv','/Users/julimpark/Downloads/produict.csv')
#     st.write(res)

# 버킷 네이머 
def bucket_namer(bucketname):
    letters_set = string.ascii_lowercase
    digits_set = string.digits
    templist = []
    for i in range(5):
        random_list1 = random.sample(letters_set+digits_set,7)
        result1 = ''.join(random_list1)
        templist.append(result1)
    templist = '-'.join(templist)
    # results = {bucketname:templist}
    return templist



#버킷 존재여부 확인
def bucket_exist(bucketname):
    try:
        s3_client.head_bucket(Bucket=bucketname)
        exists = True
    except:
        exists = False   
    return exists


#버킷 만들기
def create_bucket(bucketname):
    s3.create_bucket(Bucket=bucketname)
    # try:
    #     res = s3.create_bucket(Bucket=bucketname)
    # except:
    #     res = '이미 해당 이름의 버킷이 존재합니다.'
    # # # 버킷이 생성되었는지 확인
    # # bucket = s3.Bucket(bucketname)
    # # assert bucket.creation_date is not None
    # return res





#폴더안에 업로드
def upload_to_folder(bucketname, foldername,keyname,source):
    s3.Object(bucketname,f"{foldername}/{keyname}").upload_file(source)

#폴더파일 다운로드
def download_from_folder(bucketname, foldername,keyname,source):
    path = '/Users/julimpark/Downloads/test.py'
    key = f"{foldername}/{keyname}"
    with open(path, 'wb') as data:
        s3_client.download_fileobj(bucketname,key,data)


#폴더리스트/폴더지우기,연결등


#파일 지우기
def delete_folder_file(bucketname,foldername,filename):
    bucket = s3.Bucket(bucketname)
    for i in bucket.objects.all():
        if f"{foldername}/{filename}" == i.key:
            s3.Object(bucketname,i.key).delete()
    


    
    
# 버킷 삭제
def delete_bucket(bucketname):
    # res = s3.delete_bucket(Bucket=bucketname)
    try:
        res = s3.Bucket(bucketname).delete()
    except:
        res = "버킷이 삭제되었습니다."
    return res

# delete = st.button('delete bucket')
# if delete:
#     res =  delete_bucket('testbucket002')
#     st.write(res)
    

def get_object_inform(bucketname):
    objects = s3_client.list_objects(Bucket=bucketname)
    return objects

def get_object_inform2(bucketname):
    # buckets = s3.Bucket(bucketname)
    # files_in_bucket = list(buckets.objects.all())
    paginator = s3_client.get_paginator('list_objects')
    pages = paginator.paginate(Bucket=bucketname)#, Prefix='prefix')
    size = []
    try:
        for page in pages:
            # for obj in page['Contents']:
            size.append(page['Contents'])
                # size.append(page)
        return size
    except:
        size = []
        return size
    # return files_in_bucket
    
    

#특정 버킷 안의 파일 리스트
def files_in_bucket(bucketname):
    buckets = s3.Bucket(bucketname)
    filelist = []
    for i in buckets.objects.all():
        filelist.append(i.key)
    return filelist

#파일 이름에서 특정 문구 검색하여 리스트 추출
def filename_in_bucket(bucketname,strings):
    buckets = s3.Bucket(bucketname)
    filelist = []
    for i in buckets.objects.all():
        filelist.append(i.key)
    filtered_filelist = []
    if len(filelist)!=0:
        for i in filelist:
            if fnmatch.fnmatch(unicodedata.normalize('NFC',i), f'*{strings}*'):
                filtered_filelist.append(i)
            else:
                pass
    return filtered_filelist



def foldername_in_bucket(bucketname):
    objects = s3_client.list_objects(Bucket=bucketname)
    folders = []
    for obj in objects["Contents"]:
        if fnmatch.fnmatch(obj["Key"],'*/*'):
            temp = obj['Key'].split('/')
            # for tp in temp:
            folders.append(temp[0])
            # folders.append(obj['Key'][:-1])
    return sorted(set(folders))

# bucketlist = st.button('files in bucket')
# if bucketlist:
#     res =  files_in_bucket('testbucket001')
#     st.write(res)

# 버킷 리스트 받기
# @st.cache_data(ttl=3600)
def list_of_buckets():
    bucketlist=[]
    res = s3.buckets.all()
    for i in res:
        bucketlist.append(i.name)
    return bucketlist
# bucketlist = st.button('list of bucket')
# if bucketlist:
#     res = list_of_buckets()
#     st.write(res)
    
def make_folder(bucketname,foldername):
    s3_client.put_object(Bucket=bucketname, Key=(foldername + '/'))




#특정 버킷의 파일 사이즈 확인
def file_size_in_bucket(bucketname):
    resp = s3.Bucket(bucketname)
    size = 0
    for i in resp.objects.all():
        size += i.size
    return size
#특정 버킷의 파일 사이즈 리스트
def file_sizelist_in_bucket(bucketname):
    resp = s3.Bucket(bucketname)
    size = []
    for i in resp.objects.all():
        size.append(i.size)
    return size


# filesize = st.button('filesizes in specific bucket')
# if filesize:
#     res = file_size_in_bucket('testbucket001')
#     st.write(res)
    
# 파일이름변경
def rename_file_in_bucket(bucketname,filename,newfilename):
    copy_source = {'Bucket':bucketname,'Key':filename}
    bkt = s3.Bucket(bucketname)
    obj = bkt.Object(newfilename)
    obj.copy(copy_source)
    s3.Object(bucketname,filename).delete()
    
# renamefile = st.button('renamefile in specific bucket')
# if renamefile:
#     rename_file_in_bucket('testbucket001','etc.py','etc222.py')
    

    
#파일 옮기기
def send_another_bucket(bucketname,filename,newbucketname):
    copy_source = {'Bucket':bucketname,'Key':filename}
    bkt = s3.Bucket(newbucketname)
    obj = bkt.Object(filename)
    obj.copy(copy_source)
    s3.Object(bucketname,filename).delete()
    
    

# sendfile = st.button('sendfile in specific bucket')
# if sendfile:
#     send_another_bucket('testbucket001','etc.py','testbucket002')
    


#파일 지우기
def delete_file(bucketname,filename):
    bucket = s3.Bucket(bucketname)
    for i in bucket.objects.all():
        if filename == i.key:
            s3.Object(bucketname,i.key).delete()
        else:
            return 'error'

def delete_file_choice(bucketname,filename):
    s3.Object(bucketname,filename).delete()


# filedelete= st.button('filedelete in specific bucket')
# if filedelete:
#     res = delete_file('testbucket001','etc.py')
#     st.write(res)
    
    
#버킷 이름변경

def rename_bucket(bucketname,newbucketname):
    s3.create_bucket(Bucket=newbucketname)
    filelist = files_in_bucket(bucketname)
    for i in filelist:
        send_another_bucket(bucketname,i,newbucketname)
    s3.Bucket(bucketname).delete()

# renamebucket = st.button('renamebucket in specific bucket')
# if renamebucket:
#     rename_bucket('testbucket001','testbucket004')
    

#버킷 복사

def copy_bucket(bucketname):
    newbucketname = str(bucketname)+"copy"
    s3.create_bucket(Bucket=newbucketname)
    filelist = files_in_bucket(bucketname)
    for i in filelist:
        send_another_bucket(bucketname,i,newbucketname)

# copybucket = st.button('copybucket in specific bucket')
# if copybucket:
#     copy_bucket('testbucket004copy')
    