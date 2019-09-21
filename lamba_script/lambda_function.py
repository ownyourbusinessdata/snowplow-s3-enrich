from io import BytesIO
from user_agents import parse
from requests import get

import geoip2.database
import datetime
import tarfile
import logging
import boto3
import gzip
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    geoippath = '/tmp/GeoLite2-City.mmdb'

    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    logger.info('Reading {} from {}'.format(file_key, bucket_name))
    s3.download_file(bucket_name, file_key, '/tmp/file.zip')

    try:
        s3.download_file(bucket_name, 'GeoLite2-City.mmdb', '/tmp/GeoLite2-City.mmdb')
    except:
        url = "https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz"
        response = get(url)
        with open('/tmp/GeoLite2-City.tar.gz', 'wb') as file:
            file.write(response.content)
        geofilename = re.compile("GeoLite2-City.mmdb")
        tar = tarfile.open("/tmp/GeoLite2-City.tar.gz")
        for member in tar.getmembers():
            if geofilename.search(member.name):
                geoippath = '/tmp/' + member.name
                tar.extract(member, path='/tmp/')
        tar.close()
        s3.upload_file(geoippath, bucket_name, 'GeoLite2-City.mmdb')
    
    dtnow = datetime.datetime.now(datetime.timezone.utc)
    geoipheader = s3.head_object(Bucket=bucket_name,Key='GeoLite2-City.mmdb')
    dtdelta = dtnow - geoipheader['LastModified']
    if (dtdelta.days > 1):
        s3.delete_object(Bucket=bucket_name,Key='GeoLite2-City.mmdb')
    
    archgz = gzip.open('/tmp/file.zip')
    file_content = archgz.read()
    lines = file_content.split(b'\n')
    
    header = re.search ('#Fields: (.*)',lines[1].decode("utf-8"))
    header = header.group(1).split()
    datvalues = ""
    for l in lines[2:-1]:
        r = re.compile(r'([^\t]*)\t*')
        l = r.findall(l.decode("utf-8"))[:-1]
        collector_tstamp = l[0] + ' ' + l[1]
        refersplitter = re.compile(r'([^/]*)/*')
        referer = refersplitter.findall(l[9])[:-1]
        refr_urlscheme = referer[0][:-1]
        try:
            refr_urlhost = referer[1]
        except:
            refr_urlhost = '-'
        try:
            refr_urlpath = '/' + '/'.join(referer[2:])
        except:
            refr_urlpath = '-'
        querysplitter = re.compile(r'([^\?]*)\?*')
        qryurl = querysplitter.findall(referer[-1])[:-1]
        try:
            refr_urlquery = qryurl[1]
        except IndexError:
            refr_urlquery = '-'
        userag = l[10].replace("%2520", " ")
        useragent = userag
        userag = parse(userag)
        br_name = userag.browser.family + ' ' + userag.browser.version_string
        br_family = userag.browser.family
        br_version = userag.browser.version
        os_family = userag.os.family
        dvce_type = userag.device.family
        dvce_ismobile = userag.is_mobile
        geoipdbreader = geoip2.database.Reader(geoippath)
        user_ipaddress = l[4]
        geoipdbresult = geoipdbreader.city(l[4])
        geo_country = geoipdbresult.registered_country.iso_code
        try:
            geo_city = geoipdbresult.city.names['en']
        except:
            geo_city = '-'
        geo_zipcode = geoipdbresult.postal.code
        geo_latitude = geoipdbresult.location.latitude
        geo_longitude = geoipdbresult.location.longitude
        try:
            geo_region_name = geoipdbresult.subdivisions[0].names['en']
        except:
            geo_region_name = '-'
        geo_timezone = geoipdbresult.location.time_zone
        urisplt = re.compile(r'([^&]*)&*')
        urispltnodes = urisplt.findall(l[11])[:-1]
        spvalues = {'app_id': '-','platform': '-','collector_tstamp': collector_tstamp,'dvce_created_tstamp': '-','event': '-','event_id': '-','txn_id': '-','name_tracker': '-','v_tracker': '-','user_id': '-','user_ipaddress': user_ipaddress,'user_fingerprint': '-','domain_userid': '-','domain_sessionidx': '-','network_userid': '-','geo_country': geo_country,'geo_city': geo_city,'geo_zipcode': geo_zipcode,'geo_latitude': geo_latitude,'geo_longitude': geo_longitude,'geo_region_name': geo_region_name,'page_url': '-','page_title': '-','page_referrer': '-','refr_urlscheme': refr_urlscheme,'refr_urlhost': refr_urlhost,'refr_urlpath': refr_urlpath,'refr_urlquery': refr_urlquery,'se_category': '-','se_action': '-','se_label': '-','se_property': '-','se_value': '-','unstruct_event': '-','tr_orderid': '-','tr_affiliation': '-','tr_total': '-','tr_tax': '-','tr_shipping': '-','tr_city': '-','tr_state': '-','tr_country': '-','ti_orderid': '-','ti_sku': '-','ti_name': '-','ti_category': '-','ti_price': '-','ti_quantity': '-','pp_xoffset_min': '-','pp_xoffset_max': '-','pp_yoffset_min': '-','pp_yoffset_max': '-','useragent': useragent,'br_name': br_name,'br_family': br_family,'br_version': br_version,'br_lang': '-','br_features_pdf': '-','br_features_flash': '-','br_features_java': '-','br_features_director': '-','br_features_quicktime': '-','br_features_realplayer': '-','br_features_windowsmedia': '-','br_features_gears': '-','br_features_silverlight': '-','br_cookies': '-','br_colordepth': '-','br_viewwidth': '-','br_viewheight': '-','os_family': os_family,'os_timezone': '-','dvce_type': dvce_type,'dvce_ismobile': dvce_ismobile,'dvce_screenwidth': '-','dvce_screenheight': '-','doc_charset': '-','doc_width': '-','doc_height': '-','tr_currency': '-','ti_currency': '-','geo_timezone': geo_timezone,'dvce_sent_tstamp': '-','domain_sessionid': '-','event_vendor': '-'}
        if len(urispltnodes[0]) > 5:
            for spparams in urispltnodes:
                spsplitter = re.compile(r'([^=]*)=*')
                sp = spsplitter.findall(spparams)[:-1]
                if sp[0] == 'stm':
                   spvalues['dvce_sent_tstamp'] = sp[1]
                if sp[0] == 'e':
                   spvalues['event'] = sp[1]
                if sp[0] == 'url':
                   spvalues['page_url'] = sp[1]
                if sp[0] == 'page':
                   spvalues['page_title'] = sp[1]
                if sp[0] == 'pp_mix':
                   spvalues['pp_xoffset_min'] = sp[1]
                if sp[0] == 'pp_max':
                   spvalues['pp_xoffset_max'] = sp[1]
                if sp[0] == 'pp_miy':
                   spvalues['pp_yoffset_min'] = sp[1]
                if sp[0] == 'pp_may':
                   spvalues['pp_yoffset_max'] = sp[1]
                if sp[0] == 'tv':
                   spvalues['v_tracker'] = sp[1]
                if sp[0] == 'tna':
                   spvalues['name_tracker'] = sp[1]
                if sp[0] == 'aid':
                   spvalues['app_id'] = sp[1]
                if sp[0] == 'p':
                   spvalues['platform'] = sp[1]
                if sp[0] == 'tz':
                   spvalues['os_timezone'] = sp[1]
                if sp[0] == 'lang':
                   spvalues['br_lang'] = sp[1]
                if sp[0] == 'cs':
                   spvalues['doc_charset'] = sp[1]
                if sp[0] == 'f_pdf':
                   spvalues['br_features_pdf'] = sp[1]
                if sp[0] == 'f_qt':
                   spvalues['br_features_quicktime'] = sp[1]
                if sp[0] == 'f_realp':
                   spvalues['br_features_realplayer'] = sp[1]
                if sp[0] == 'f_wma':
                   spvalues['br_features_windowsmedia'] = sp[1]
                if sp[0] == 'f_dir':
                   spvalues['br_features_director'] = sp[1]
                if sp[0] == 'f_fla':
                   spvalues['br_features_flash'] = sp[1]
                if sp[0] == 'f_java':
                   spvalues['br_features_java'] = sp[1]
                if sp[0] == 'f_gears':
                   spvalues['br_features_gears'] = sp[1]
                if sp[0] == 'f_ag':
                   spvalues['br_features_silverlight'] = sp[1]
                if sp[0] == 'res':
                   ressplitter = re.compile(r'([^x]*)x*')
                   res = ressplitter.findall(sp[1])[:-1]
                   spvalues['dvce_screenheight'] = res[1]
                   spvalues['dvce_screenwidth'] = res[0]
                   continue
                if sp[0] == 'cd':
                   spvalues['br_colordepth'] = sp[1]
                if sp[0] == 'cookie':
                   spvalues['br_cookies'] = sp[1]
                if sp[0] == 'eid':
                   spvalues['event_id'] = sp[1]
                if sp[0] == 'dtm':
                   spvalues['dvce_created_tstamp'] = sp[1]
                if sp[0] == 'vp':
                   ressplitter = re.compile(r'([^x]*)x*')
                   brdim = ressplitter.findall(sp[1])[:-1]
                   spvalues['br_viewwidth'] = brdim[1]
                   spvalues['br_viewheight'] = brdim[0]
                   continue
                if sp[0] == 'ds':
                   ressplitter = re.compile(r'([^x]*)x*')
                   docdim = ressplitter.findall(sp[1])[:-1]
                   spvalues['doc_width'] = docdim[1]
                   spvalues['doc_height'] = docdim[0]
                   continue
                if sp[0] == 'vid':
                   spvalues['domain_sessionidx'] = sp[1]
                if sp[0] == 'sid':
                   spvalues['domain_sessionid'] = sp[1]
                if sp[0] == 'duid':
                   spvalues['domain_userid'] = sp[1]
                if sp[0] == 'fp':
                   spvalues['user_fingerprint'] = sp[1]
                if sp[0] == 'ue_px':
                   spvalues['unstruct_event'] = sp[1]
                if sp[0] == 'refr':
                   spvalues['page_referrer'] = sp[1]
                if sp[0] == 'tid':
                   spvalues['txn_id'] = sp[1]
                if sp[0] == 'uid':
                   spvalues['user_id'] = sp[1]
                if (sp[0] == 'nuid') or (sp[0] == 'tnuid'):
                   spvalues['network_userid'] = sp[1]
                if sp[0] == 'se_ca':
                   spvalues['se_category'] = sp[1]
                if sp[0] == 'se_ac':
                   spvalues['se_action'] = sp[1]
                if sp[0] == 'se_la':
                   spvalues['se_label'] = sp[1]
                if sp[0] == 'se_pr':
                   spvalues['se_property'] = sp[1]
                if sp[0] == 'se_va':
                   spvalues['se_value'] = sp[1]
                if sp[0] == 'tr_id':
                   spvalues['tr_orderid'] = sp[1]
                if sp[0] == 'tr_af':
                   spvalues['tr_affiliation'] = sp[1]
                if sp[0] == 'tr_tt':
                   spvalues['tr_total'] = sp[1]
                if sp[0] == 'tr_tx':
                   spvalues['tr_tax'] = sp[1]
                if sp[0] == 'tr_sh':
                   spvalues['tr_shipping'] = sp[1]
                if sp[0] == 'tr_ci':
                   spvalues['tr_city'] = sp[1]
                if sp[0] == 'tr_st':
                   spvalues['tr_state'] = sp[1]
                if sp[0] == 'tr_co':
                   spvalues['tr_country'] = sp[1]
                if sp[0] == 'ti_id':
                   spvalues['ti_orderid'] = sp[1]
                if sp[0] == 'ti_sk':
                   spvalues['ti_sku'] = sp[1]
                if sp[0] == 'ti_na':
                   spvalues['ti_name'] = sp[1]
                if sp[0] == 'ti_ca':
                   spvalues['ti_category'] = sp[1]
                if sp[0] == 'ti_pr':
                   spvalues['ti_price'] = sp[1]
                if sp[0] == 'ti_qu':
                   spvalues['ti_quantity'] = sp[1]
                if sp[0] == 'tr_cu':
                   spvalues['tr_currency'] = sp[1]
                if sp[0] == 'ti_cu':
                   spvalues['ti_currency'] = sp[1]
                if sp[0] == 'evn':
                   spvalues['event_vendor'] = sp[1]
            for key,val in spvalues.items():
                datvalues = datvalues + str(val) + '\t'
            datvalues = datvalues + '\n'
    if len(urispltnodes[0]) > 5:
        gz_body = BytesIO()
        gz = gzip.GzipFile(None, 'wb', 9, gz_body)
        gz.write(datvalues.encode('utf-8'))
        gz.close()
        s3.put_object(Bucket=bucket_name, Key=file_key.replace("RAW", "Converted"),  ContentType='text/plain',  ContentEncoding='gzip',  Body=gz_body.getvalue())
