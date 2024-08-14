from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from QIT.utils.APICode import APICodeClass
from rest_framework import status
from QIT.serializers import CompanyMasterDetailsGetSerializer, MAProfileSerializer
from QIT.models import QitCompany, QitMasteradmin
from django.core.cache import cache
import json
from dotenv import load_dotenv
import os
load_dotenv()
from .common import create_userlogin

@csrf_exempt
@api_view(['GET'])
def getCmpDetails(request):
    try:
        companies = QitCompany.objects.all()
        serializer = CompanyMasterDetailsGetSerializer(companies, many=True)
        return Response({
            'data':serializer.data,
            'APICode':APICodeClass.Master_Admin_CmpStatus.value
        }, status=status.HTTP_200_OK)
    except QitCompany.DoesNotExist:
        return Response({
            'Status': 400,
            'StatusMsg': "Data not found",
            'APICode':APICodeClass.Master_Admin_CmpStatus.value
        },status=400)  
    except Exception as e:
        return Response({
            'Status': 400,
            'StatusMsg': "Error : " + str(e),
            'APICode':APICodeClass.Master_Admin_CmpStatus.value
        },status=400)  
    
@csrf_exempt
@api_view(["POST"])
def ActiveComapny(request):
    try:
        reqData = request.data
        if reqData["status"] != "I" and reqData["status"] != "A":
            return Response({'Status': 400, 'StatusMsg': "Enter valid status",'APICode':APICodeClass.Master_Admin_CmpStatus.value}, status=400)  
        if reqData["status"] == "I" and reqData["reason"] == "":
            return Response({'Status': 400, 'StatusMsg': "Reason is required",'APICode':APICodeClass.Master_Admin_CmpStatus.value}, status=400) 
        resDB = QitCompany.objects.get(transid = reqData["cmpid"])
        if resDB:
            statusData = ""
            if reqData["status"] == "A":
                statusData = "Activated"
            if reqData["status"] == "I": 
                statusData = "Inactivated"

            if str(resDB.status) == str(reqData["status"]):
                return Response({'Status': 400, 'StatusMsg': f"Company Already {statusData}",'APICode':APICodeClass.Master_Admin_CmpStatus.value}, status=400)      
            
            resDB.status = reqData["status"]
            resDB.reason = reqData["reason"]
            resDB.save()
            return Response({
                'Status':200,
                'StatusMsg':f"Company is {statusData}",
                'APICode':APICodeClass.Master_Admin_CmpStatus.value
            })
        else:
            return Response({
                'Status':400,
                'StatusMsg':"Invalid Company id.",
                'APICode':APICodeClass.Master_Admin_CmpStatus.value
            },status=400)
    except QitCompany.DoesNotExist:
        return Response({
            'Status':400,
            'StatusMsg':"Company data not found.",
            'APICode':APICodeClass.Master_Admin_CmpStatus.value
        },status=400)
    except Exception as e:
        return Response({
            'Status':400,
            'StatusMsg':str(e),
            'APICode':APICodeClass.Master_Admin_CmpStatus.value
        },status=400)

@csrf_exempt
@api_view(['POST'])
def saveMasterAdminDetails(request):
    body_data = request.data
    try:
        if not body_data["e_mail"]:
            return Response({
                'Status':400,
                'StatusMsg':"Email is required",
                'APICode':APICodeClass.Master_Admin_Save.value
            },status=400)
        if not body_data["password"]:
            return Response({
                'Status':400,
                'StatusMsg':"Password is required",
                'APICode':APICodeClass.Master_Admin_Save.value
            },status=400)
        if not body_data["bname"]:
            return Response({
                'Status':400,
                'StatusMsg':"BusinessName is required",
                'APICode':APICodeClass.Master_Admin_Save.value
            },status=400)
        if not body_data["blocation"]:
            return Response({
                'Status':400,
                'StatusMsg':"BusinessLocation is required",
                'APICode':APICodeClass.Master_Admin_Save.value
            },status=400)
        
        emailExistInComapny = QitMasteradmin.objects.filter(e_mail = body_data["e_mail"])
        if(emailExistInComapny):
            return Response({
                'Status':400,
                'StatusMsg':"This email alredy register as Master Admin",
                'APICode':APICodeClass.Master_Admin_Save.value
            },status=400)
        
        stored_data_json = cache.get(f"otp_{body_data['e_mail']}")
        if stored_data_json:
            stored_data = json.loads(stored_data_json)
            stored_status = stored_data['status']
            stored_role = stored_data['role']
            if stored_status == 1 and stored_role.upper() == "MA" :
                res = QitMasteradmin.objects.create(e_mail=body_data["e_mail"], password=body_data["password"], bname=body_data["bname"], blocation=body_data["blocation"])
                create_userlogin(body_data["e_mail"],body_data["password"],"MA")
                return Response({
                    'status': status.HTTP_201_CREATED,
                    'StatusMsg':"Registered successfully",
                    'APICode':APICodeClass.Master_Admin_Save.value
                })
            else:
                response = {
                    'Status': 400,
                    'StatusMsg': "OTP is not verified",
                    'APICode':APICodeClass.Master_Admin_Save.value
                }
                return Response(response,status=400)
        else:
            response = {
                    'Status': 400,
                    'StatusMsg': "Email not found or OTP expired",
                    'APICode':APICodeClass.Master_Admin_Save.value
                }
            return Response(response,status=400)
    except Exception as e:
        return Response({
            'Status': 400,
            'StatusMsg': "Error : " + str(e),
            'APICode':APICodeClass.Master_Admin_Save.value
        },status=400)  
    

@csrf_exempt
@api_view(["GET"])
def GetComapnyDataById(request,cid):
    try:
        resDB = QitMasteradmin.objects.get(transid = cid)
        serializer = MAProfileSerializer(resDB,many=False)
        if resDB:
            return Response({
                'Data':serializer.data,
                'APICode':APICodeClass.Master_Admin_Get.value
            })
        else:
            return Response({
                'Status':400,
                'StatusMsg':"Invalid Company id",
                'APICode':APICodeClass.Master_Admin_Get.value
            },status=400)
    except QitCompany.DoesNotExist:
        return Response({
            'Status':400,
            'StatusMsg':"Company data not found.",
            'APICode':APICodeClass.Master_Admin_Get.value
        },status=400)
    except Exception as e:
        return Response({
            'Status':400,
            'StatusMsg':str(e),
            'APICode':APICodeClass.Master_Admin_Get.value
        },status=400)
      
@csrf_exempt
@api_view(["PUT"])
def EditMAComapnyDataById(request):
    try:
        reqData = request.data
        resDB = QitMasteradmin.objects.get(transid = reqData["transid"])
        if resDB:
            resDB.bname = reqData["bname"]
            resDB.blocation = reqData["blocation"]
            resDB.zipcode = reqData["zipcode"]
            resDB.city = reqData["city"]
            resDB.state = reqData["state"]
            resDB.country = reqData["country"]
            resDB.phone1 = reqData["phone1"]
            resDB.phone2 = reqData["phone2"]
            resDB.websitelink = reqData["websitelink"]
            resDB.cmplogo = reqData["cmplogo"]
            resDB.save()
            return Response({
                'Status':200,
                'StatusMsg':"Company data updated",
                'APICode':APICodeClass.Master_Admin_Edit.value
            })
        else:
            return Response({
                'Status':400,
                'StatusMsg':"Invalid Company id",
                'APICode':APICodeClass.Master_Admin_Edit.value
            },status=400)
    except QitMasteradmin.DoesNotExist:
        return Response({
            'Status':400,
            'StatusMsg':"Master admin data not found.",
            'APICode':APICodeClass.Master_Admin_Edit.value
        },status=400)
    except Exception as e:
        return Response({
            'Status':400,
            'StatusMsg':str(e),
            'APICode':APICodeClass.Master_Admin_Edit.value
        },status=400)
    