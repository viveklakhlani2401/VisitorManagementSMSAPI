from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from QIT.models import QitUsermaster, QitAuthenticationrule,QitCompany,QitNotificationrule,QitNotificationmaster,QitUserlogin,QitMasteradmin,QitMaNotification
from QIT.serializers import GetDataClassSerializer,GetRuleClassSerializer,SetNotificationClassSerializer,GetNotificationClassSerializer,ReadNotificationClassSerializer,GetPreSetDataClassSerializer,SetSaNotificationClassSerializer
import logging
import ast
from datetime import datetime
from django.db import transaction
from .common import email_wise_data_filter,role_email_get_data,send_notification,time_since,send_sa_notification
from QIT.utils.APICode import APICodeClass

logger = logging.getLogger(__name__)

@api_view(['POST'])
def SaveNotificationRule(request):
    logger.info("Received data: %s", request.data)
    serializer = GetDataClassSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.error("Invalid data: %s", serializer.errors)
        return Response({
            'StatusCode': '400', 
            'IsSaved': 'N', 
            'StatusMsg': 'Invalid Data',
            'APICode':APICodeClass.Notification_Rule_Save.value
        }, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    useremail = data['useremail']
    user_role = data['userrole']
    cmptransid = data['cmptransid']
    module_classes = data['module_classes']

    try:
        logger.info("Calling notification_master: SaveNotificationRule()")
        cmpcheck = user = QitCompany.objects.filter(transid=cmptransid).first()
        if not cmpcheck:
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'Invalid company',
                'APICode':APICodeClass.Notification_Rule_Save.value
            }, status=status.HTTP_400_BAD_REQUEST)
        user = None
        cmptransidUser = None
        if 'COMPANY' in data['userrole'].upper():
            user = QitCompany.objects.filter(e_mail=useremail).first()
            if not user:
                logger.info("Calling authorization_master saved rule: GetAuthRule(): Error User not found")
                return Response({
                    'StatusCode': '400', 
                    'IsSaved': 'N', 
                    'StatusMsg': 'Company Not found',
                    'APICode':APICodeClass.Notification_Rule_Save.value
                }, status=status.HTTP_400_BAD_REQUEST)
            cmptransidUser = user
        elif 'USER' in data['userrole'].upper():
            user = QitUsermaster.objects.filter(e_mail=useremail).first()
            if not user:
                logger.info("Calling authorization_master saved rule: GetAuthRule(): Error User not found")
                return Response({
                    'StatusCode': '400', 
                    'IsSaved': 'N', 
                    'StatusMsg': 'User Not found',
                    'APICode':APICodeClass.Notification_Rule_Save.value
                }, status=status.HTTP_400_BAD_REQUEST)
            cmptransidUser = user.cmptransid
        if not user:
            logger.info("Calling notification_master saved rule: SaveNotificationRule(): Error User not found")
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'User Not found',
                'APICode':APICodeClass.Notification_Rule_Save.value
            }, status=status.HTTP_400_BAD_REQUEST)
        if str(cmptransidUser.transid).strip() != str(cmptransid).strip():
            logger.info("Calling notification_master saved rule: SaveNotificationRule(): Error Invalid company user")
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'Invalid company user',
                'APICode':APICodeClass.Notification_Rule_Save.value
            }, status=status.HTTP_400_BAD_REQUEST)

        ar_data = module_classes

        existing_rule = QitNotificationrule.objects.filter(user_id=user.transid,userrole=data['userrole'].upper()).first()

        if existing_rule:
            existing_rule.n_rule_detail = ar_data
            existing_rule.save()
        else:
            new_rule = QitNotificationrule(user_id=user.transid,cmptransid=cmptransidUser, n_rule_detail=ar_data,userrole=data['userrole'].upper())
            new_rule.save()

        logger.info("Calling notification_master saved rule: SaveNotificationRule()")
        return Response({
            'StatusCode': '200', 
            'IsSaved': 'Y', 
            'StatusMsg': 'Saved Successfully!!!',
            'APICode':APICodeClass.Notification_Rule_Save.value
        }, status=status.HTTP_200_OK)
    except Exception as ex:
        logger.error("Calling notification_master Error: SaveNotificationRule() " + str(ex))
        return Response({
            'StatusCode': '400', 
            'IsSaved': 'N', 
            'StatusMsg': str(ex),
            'APICode':APICodeClass.Notification_Rule_Save.value
        }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def NotificationPreSetRule(request):
    logger.info("Received data: %s", request.data)
    serializer = GetPreSetDataClassSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.error("Invalid data: %s", serializer.errors)
        return Response({
            'StatusCode': '400', 
            'IsSaved': 'N', 
            'StatusMsg': 'Invalid Data',
            'APICode':APICodeClass.Notification_Rule_Preset.value
        }, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    fromUseremail = data['fromUseremail']
    userrole = data['userrole']
    toUsers = data['toUsers']
    cmptransid = data['cmptransid']

    try:
        logger.info("Calling notification_master: SaveNotificationRule()")
        cmpcheck = user = QitCompany.objects.filter(transid=cmptransid).first()
        if not cmpcheck:
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'Invalid company',
                'APICode':APICodeClass.Notification_Rule_Preset.value
            }, status=status.HTTP_400_BAD_REQUEST)
        user = None
        cmptransidUser = None
        if 'COMPANY' in userrole.upper():
            user = QitCompany.objects.filter(e_mail=fromUseremail).first()
            if not user:
                logger.info("Calling authorization_master saved rule: GetAuthRule(): Error User not found")
                return Response({
                    'StatusCode': '400', 
                    'IsSaved': 'N', 
                    'StatusMsg': 'Company Not found',
                    'APICode':APICodeClass.Notification_Rule_Preset.value
                }, status=status.HTTP_400_BAD_REQUEST)
            cmptransidUser = user
        elif 'USER' in userrole.upper():
            user = QitUsermaster.objects.filter(e_mail=fromUseremail).first()
            if not user:
                logger.info("Calling authorization_master saved rule: GetAuthRule(): Error User not found")
                return Response({
                    'StatusCode': '400', 
                    'IsSaved': 'N', 
                    'StatusMsg': 'User Not found',
                    'APICode':APICodeClass.Notification_Rule_Preset.value
                }, status=status.HTTP_400_BAD_REQUEST)
            cmptransidUser = user.cmptransid
        if not user:
            logger.info("Calling notification_master saved rule: SaveNotificationRule(): Error User not found")
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'User Not found',
                'APICode':APICodeClass.Notification_Rule_Preset.value
            }, status=status.HTTP_400_BAD_REQUEST)
        if str(cmptransidUser.transid).strip() != str(cmptransid).strip():
            logger.info("Calling notification_master saved rule: SaveNotificationRule(): Error Invalid company user")
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'Invalid company user',
                'APICode':APICodeClass.Notification_Rule_Preset.value
            }, status=status.HTTP_400_BAD_REQUEST)

        ar_data = []

        existing_rule = QitNotificationrule.objects.filter(user_id=user.transid).first()

        if existing_rule:
            ar_data = existing_rule.n_rule_detail
            for user in toUsers :
                userData = role_email_get_data(user['useremail'],user['userrole'])
                existing_rule = QitNotificationrule.objects.filter(user_id=userData.transid).first()

                if existing_rule:
                    existing_rule.n_rule_detail = ar_data
                    existing_rule.save()
                else:
                    preset_rule = QitNotificationrule(user_id=userData.transid,cmptransid=userData.cmptransid, n_rule_detail=ar_data,userrole=userData.usertype.upper())
                    preset_rule.save()
            return Response({
                'StatusCode': '200', 
                'IsSaved': 'Y', 
                'StatusMsg': 'Saved Successfully!!!',
                'APICode':APICodeClass.Notification_Rule_Preset.value
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'No Rule Found',
                'APICode':APICodeClass.Notification_Rule_Preset.value
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Calling notification_master Error: SaveNotificationRule() " + str(ex))
        return Response({
            'StatusCode': '400', 
            'IsSaved': 'N', 
            'StatusMsg': str(ex),
            'APICode':APICodeClass.Notification_Rule_Preset.value
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def GetNotificationRule(request):
    logger.info("Received data: %s", request.data)
    serializer = GetRuleClassSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.error("Invalid data: %s", serializer.errors)
        return Response({
            'StatusCode': '400', 
            'IsSaved': 'N', 
            'StatusMsg': 'Invalid Data',
            'APICode':APICodeClass.Notification_Rule_Get.value
        }, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    useremail = data['useremail']
    user_role = data['userrole']
    cmptransid = data['cmptransid']

    try:
        logger.info("Calling notification_master: GetNotificationRule()")
        cmpcheck = user = QitCompany.objects.filter(transid=cmptransid).first()
        if not cmpcheck:
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'Invalid company',
                'APICode':APICodeClass.Notification_Rule_Get.value
            }, status=status.HTTP_400_BAD_REQUEST)
        user = None
        cmptransidUser = None
        if 'COMPANY' in data['userrole'].upper():
            user = QitCompany.objects.filter(e_mail=useremail).first()
            if not user:
                logger.info("Calling authorization_master saved rule: GetAuthRule(): Error User not found")
                return Response({
                    'StatusCode': '400', 
                    'IsSaved': 'N', 
                    'StatusMsg': 'Company Not found',
                    'APICode':APICodeClass.Notification_Rule_Get.value
                }, status=status.HTTP_400_BAD_REQUEST)
            cmptransidUser = user
        elif 'USER' in data['userrole'].upper():
            user = QitUsermaster.objects.filter(e_mail=useremail).first()
            if not user:
                logger.info("Calling authorization_master saved rule: GetAuthRule(): Error User not found")
                return Response({
                    'StatusCode': '400', 
                    'IsSaved': 'N', 
                    'StatusMsg': 'User Not found',
                    'APICode':APICodeClass.Notification_Rule_Get.value
                }, status=status.HTTP_400_BAD_REQUEST)
            cmptransidUser = user.cmptransid
        if not user:
            logger.info("Calling notification_master saved rule: GetNotificationRule(): Error User not found")
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'User Not found',
                'APICode':APICodeClass.Notification_Rule_Get.value
            }, status=status.HTTP_400_BAD_REQUEST)
        if str(cmptransidUser.transid).strip() != str(cmptransid).strip():
            logger.info("Calling notification_master saved rule: GetNotificationRule(): Error Invalid company user")
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'Invalid company user',
                'APICode':APICodeClass.Notification_Rule_Get.value
            }, status=status.HTTP_400_BAD_REQUEST)
       
        existing_rule = QitNotificationrule.objects.filter(user_id=user.transid,cmptransid=cmptransid).first()

        if existing_rule:
            return Response({
                'StatusCode': '200', 
                'IsSaved': 'Y', 
                'Notification_Rule': existing_rule.n_rule_detail,
                'APICode':APICodeClass.Notification_Rule_Get.value
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'No Rule Found',
                'APICode':APICodeClass.Notification_Rule_Get.value
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as ex:
        logger.error("Calling notification_master Error: GetNotificationRule() " + str(ex))
        return Response({
            'StatusCode': '400', 
            'IsSaved': 'N', 
            'StatusMsg': str(ex),
            'APICode':APICodeClass.Notification_Rule_Get.value
        }, status=status.HTTP_400_BAD_REQUEST)

def chk_user_comp_id(user_email):
    user  = QitUserlogin.objects.filter(e_mail=user_email).first()
    if user:
        return user
    else:
        return None
    
@api_view(['POST'])
def SaveNotification(request):
    try:
        data = request.data
        serializer = SetNotificationClassSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                "StatusCode": "400", 
                "StatusMsg": "Payload is empty or invalid",
                'APICode':APICodeClass.Notification_Get.value
            }, status=status.HTTP_400_BAD_REQUEST)
        
        notification = serializer.validated_data
        module = notification.get('module')
        cmptransid = notification.get('cmptransid')
        cmpcheck = QitCompany.objects.filter(transid=cmptransid).first()
        if not cmpcheck:
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'Invalid company',
                'APICode':APICodeClass.Notification_Get.value
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if module == '':
            return Response({
                "StatusCode": "403", 
                "IsSaved": "N", 
                "StatusMsg": "Notification Module is required",
                'APICode':APICodeClass.Notification_Get.value
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_ids = []
        all_rules = QitNotificationrule.objects.filter(cmptransid=notification.get('cmptransid'))
        for rule in all_rules:
            rule_detail_str = rule.n_rule_detail.decode('utf-8') if isinstance(rule.n_rule_detail, bytes) else rule.n_rule_detail
            rule_detail_list = ast.literal_eval(rule_detail_str)
            i = 0
            for details in rule_detail_list:
                i = i+1
                if details.get('text') == module and details.get('hasAccess'):
                    userdata = email_wise_data_filter(rule.user_id, rule.userrole,notification.get('cmptransid'))
                    user_id = chk_user_comp_id(userdata.e_mail)
                    user_ids.append(user_id)
                    break

        if not user_ids:
            return Response({
                "StatusCode": "404", 
                "StatusMsg": "No users found for the specified module.",
                'APICode':APICodeClass.Notification_Get.value
            }, status=status.HTTP_404_NOT_FOUND)
        print("user_ids : ",user_ids)
        if notification['sender_email'] != "0":
            sender_user = QitUserlogin.objects.filter(e_mail=notification['sender_email']).first()
            if not sender_user:
                return Response({
                    "StatusCode": "404", 
                    "StatusMsg": "Sender user not found.",
                    'APICode':APICodeClass.Notification_Get.value
                }, status=status.HTTP_404_NOT_FOUND)
            else:
                sender_user=sender_user.transid
        else:
            sender_user = 0
        # sender_user_data = role_email_get_data(sender_user.e_mail,sender_user.userrole)
        new_notifications = []
        with transaction.atomic():
            for user_id in user_ids: 
                if user_id is not None:
                    notification_entity = QitNotificationmaster(
                        sender_user_id=sender_user,
                        receiver_user_id=user_id.transid,
                        notification_text=notification['notification_text'],
                        cmptransid=cmpcheck,
                        n_date_time=datetime.now(),
                        chk_status='P'
                    )
                    notification_entity.save()
                    new_notifications.append(notification_entity)
        send_notification(new_notifications,cmpcheck.transid)
        return Response({
            "StatusCode": "200", 
            "IsSaved": "Y", 
            "StatusMsg": "Notification Added successfully..",
            'APICode':APICodeClass.Notification_Get.value
        }, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({
            "StatusCode": "400", 
            "StatusMsg": str(ex),
            'APICode':APICodeClass.Notification_Get.value
        }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def SaveSaNotification(request):
    try:
        data = request.data
        serializer = SetSaNotificationClassSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                "StatusCode": "400", 
                "StatusMsg": "Payload is empty or invalid",
                'APICode':APICodeClass.Notification_Get.value
            }, status=status.HTTP_400_BAD_REQUEST)
        
        notification = serializer.validated_data
       
        user_ids = []
        cmpid_data = 0
        all_users = QitMasteradmin.objects.filter()
        for user in all_users:
            cmpid_data = user.transid
            user_id = chk_user_comp_id(user.e_mail)
            user_ids.append(user_id)
            break
                
        if not user_ids:
            return Response({
                "StatusCode": "404", 
                "StatusMsg": "No users found for the specified module.",
                'APICode':APICodeClass.Notification_Get.value
            }, status=status.HTTP_404_NOT_FOUND)
        print("user_ids : ",user_ids)
        
        SaUser  = QitMasteradmin.objects.filter(transid=cmpid_data).first()
        # print("Sa_User : ",SaUser.e_mail)
        # sender_user_data = role_email_get_data(sender_user.e_mail,sender_user.userrole)
        new_notifications = []
        with transaction.atomic():
            for user_id in user_ids: 
                if user_id is not None:
                    notification_entity = QitMaNotification(
                        cmptransid=SaUser.transid,
                        receiver_ma_id=user_id.transid,
                        notification_text=notification['notification_text'],
                        n_date_time=datetime.now(),
                        chk_status='P'
                    )
                    notification_entity.save()
                    new_notifications.append(notification_entity)
        send_sa_notification(new_notifications,cmpid_data)
        return Response({
            "StatusCode": "200", 
            "IsSaved": "Y", 
            "StatusMsg": "Notification Added successfully..",
            'APICode':APICodeClass.Notification_Get.value
        }, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({
            "StatusCode": "400", 
            "StatusMsg": str(ex),
            'APICode':APICodeClass.Notification_Get.value
        }, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def GetNotification(request):
    try:
        data = request.data
        serializer = GetNotificationClassSerializer(data=data)
        if not serializer.is_valid():
            return Response({"StatusCode": "400", "StatusMsg": "Payload is empty or invalid"}, status=status.HTTP_400_BAD_REQUEST)
        
        notification = serializer.validated_data
        email = notification.get('email')
        cmptransid = notification.get('cmptransid')
        cmpcheck = QitCompany.objects.filter(transid=cmptransid).first()
        if not cmpcheck:
            return Response({'StatusCode': '400', 'IsSaved': 'N', 'StatusMsg': 'Invalid company'}, status=status.HTTP_400_BAD_REQUEST)
        _user = QitUserlogin.objects.filter(e_mail=email).first()
        if not _user:
            return Response({"StatusCode": "404", "StatusMsg": "user not found."}, status=status.HTTP_404_NOT_FOUND)

        notifications = QitNotificationmaster.objects.filter(
            receiver_user_id = _user.transid,
            cmptransid = cmptransid
        ).values('transid', 'notification_text', 'n_date_time', 'chk_status').order_by('-n_date_time')
        for notification in notifications:
            if 'n_date_time' in notification:
                notification['n_date_time'] = time_since(notification['n_date_time'])
        return Response({"StatusCode": "200", "notifications": notifications}, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"StatusCode": "400", "StatusMsg": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def ReadNotification(request):
    try:
        data = request.data
        serializer = ReadNotificationClassSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                "StatusCode": "400", 
                "StatusMsg": "Payload is empty or invalid",
                'APICode':APICodeClass.Notification_Read.value
            }, status=status.HTTP_400_BAD_REQUEST)
        
        notification = serializer.validated_data
        transid = notification.get('transid')
        email = notification.get('email')
        cmptransid = notification.get('cmptransid')
        cmpcheck = QitCompany.objects.filter(transid=cmptransid).first()
        if not cmpcheck:
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'Invalid company',
                'APICode':APICodeClass.Notification_Read.value
            }, status=status.HTTP_400_BAD_REQUEST)
        _user = QitUserlogin.objects.filter(e_mail=email).first()
        if not _user:
            return Response({
                "StatusCode": "404", 
                "StatusMsg": "user not found.",
                'APICode':APICodeClass.Notification_Read.value
            }, status=status.HTTP_404_NOT_FOUND)

        notifications = QitNotificationmaster.objects.filter(
            transid=transid,
            receiver_user_id = _user.transid,
            cmptransid = cmptransid
        ).first()
        if notifications is not None:
            if notifications.chk_status == 'A':
                return Response({
                    "StatusCode": "404", 
                    "StatusMsg": "Notification already read.",
                    'APICode':APICodeClass.Notification_Read.value
                }, status=status.HTTP_404_NOT_FOUND)
            notifications.chk_status = 'A'
            notifications.save()
            return Response({
                "StatusCode": "200", 
                "IsSaved": "Y", 
                "StatusMsg": "Notification Read successfully..",
                'APICode':APICodeClass.Notification_Read.value
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "StatusCode": "404", 
                "StatusMsg": "Notification not found.",
                'APICode':APICodeClass.Notification_Read.value
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as ex:
        return Response({
            "StatusCode": "400", 
            "StatusMsg": str(ex),
            'APICode':APICodeClass.Notification_Read.value
        }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def GetSaNotification(request):
    try:
        data = request.data
        serializer = GetNotificationClassSerializer(data=data)
        if not serializer.is_valid():
            return Response({"StatusCode": "400", "StatusMsg": "Payload is empty or invalid"}, status=status.HTTP_400_BAD_REQUEST)
        
        notification = serializer.validated_data
        email = notification.get('email')
        cmptransid = notification.get('cmptransid')
        cmpcheck = QitMasteradmin.objects.filter(transid=cmptransid).first()
        if not cmpcheck:
            return Response({'StatusCode': '400', 'IsSaved': 'N', 'StatusMsg': 'Invalid company'}, status=status.HTTP_400_BAD_REQUEST)
        _user = QitUserlogin.objects.filter(e_mail=email).first()
        if not _user:
            return Response({"StatusCode": "404", "StatusMsg": "user not found."}, status=status.HTTP_404_NOT_FOUND)

        notifications = QitMaNotification.objects.filter(
            receiver_ma_id = _user.transid,
            cmptransid = cmptransid
        ).values('transid', 'notification_text', 'n_date_time', 'chk_status').order_by('-n_date_time')
        for notification in notifications:
            if 'n_date_time' in notification:
                notification['n_date_time'] = time_since(notification['n_date_time'])
        return Response({"StatusCode": "200", "notifications": notifications}, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"StatusCode": "400", "StatusMsg": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def ReadSaNotification(request):
    try:
        data = request.data
        serializer = ReadNotificationClassSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                "StatusCode": "400", 
                "StatusMsg": "Payload is empty or invalid",
                'APICode':APICodeClass.Notification_Read.value
            }, status=status.HTTP_400_BAD_REQUEST)
        
        notification = serializer.validated_data
        transid = notification.get('transid')
        email = notification.get('email')
        cmptransid = notification.get('cmptransid')
        cmpcheck = QitMasteradmin.objects.filter(transid=cmptransid).first()
        print("cmpcheck : ",cmpcheck)
        if not cmpcheck:
            return Response({
                'StatusCode': '400', 
                'IsSaved': 'N', 
                'StatusMsg': 'Invalid company',
                'APICode':APICodeClass.Notification_Read.value
            }, status=status.HTTP_400_BAD_REQUEST)
        _user = QitUserlogin.objects.filter(e_mail=email).first()
        if not _user:
            return Response({
                "StatusCode": "404", 
                "StatusMsg": "user not found.",
                'APICode':APICodeClass.Notification_Read.value
            }, status=status.HTTP_404_NOT_FOUND)

        notifications = QitMaNotification.objects.filter(
            transid=transid,
            receiver_ma_id = _user.transid,
            cmptransid = cmptransid
        ).first()
        if notifications is not None:
            if notifications.chk_status == 'A':
                return Response({
                    "StatusCode": "404", 
                    "StatusMsg": "Notification already read.",
                    'APICode':APICodeClass.Notification_Read.value
                }, status=status.HTTP_404_NOT_FOUND)
            notifications.chk_status = 'A'
            notifications.save()
            return Response({
                "StatusCode": "200", 
                "IsSaved": "Y", 
                "StatusMsg": "Notification Read successfully..",
                'APICode':APICodeClass.Notification_Read.value
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "StatusCode": "404", 
                "StatusMsg": "Notification not found.",
                'APICode':APICodeClass.Notification_Read.value
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as ex:
        return Response({
            "StatusCode": "400", 
            "StatusMsg": str(ex),
            'APICode':APICodeClass.Notification_Read.value
        }, status=status.HTTP_400_BAD_REQUEST)
