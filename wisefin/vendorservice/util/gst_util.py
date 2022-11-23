class GstStateCode:
    Jammu_and_Kashmir = '01'
    Himachal_Pradesh = '02'
    Punjab = '03'
    Chandigarh = '04'
    Uttarakhand = '05'
    Haryana = '06'
    Delhi = '07'
    Rajasthan = '08'
    Uttar_Pradesh = '09'
    Bihar = '10'
    Sikkim = '11'
    Arunachal_Pradesh = '12'
    Nagaland = '13'
    Manipur = '14'
    Mizoram = '15'
    Tripura = '16'
    Meghalaya = '17'
    Assam = '18'
    West_Bengal = '19'
    Jharkhand = '20'
    Odisha = '21'
    Chattisgarh = '22'
    Madhya_Pradesh = '23'
    Gujarat = '24'
    Daman_and_Diu = '25'
    Dadra_and_Nagar_Haveli = '26'
    Maharashtra = '27'
    Andhra_Pradesh = '28'
    Karnataka = '29'
    Goa = '30'
    Lakshadweep_Islands = '31'
    Kerala = '32'
    Tamil_Nadu = '33'
    Pondicherry = '34'
    Andaman_and_Nicobar_Islands = '35'
    Telangana = '36'
    Andhra_Pradesh_new = '37'
    Ladakh = '38'


class StateName:
    Andaman_Nicobar = 'Andaman Nicobar'
    Andhra_Pradesh = 'Andhra Pradesh'
    Arunachal_Pradesh = 'Arunachal Pradesh'
    Assam = 'Assam'
    Bihar = 'Bihar'
    Chandigarh = 'Chandigarh'
    Chattisgarh = 'Chattisgarh'
    Dadra_Nagar_Haveli_Daman_Diu = 'Dadra Nagar Haveli & Daman Diu'
    Delhi = 'Delhi'
    Goa = 'Goa'
    Gujarat = 'Gujarat'
    Haryana = 'Haryana'
    Himachal_Pradesh = 'Himachal Pradesh'
    Jammu_Kashmir = 'Jammu Kashmir'
    Jharkhand = 'Jharkhand'
    Karnataka = 'Karnataka'
    Kerala = 'Kerala'
    Ladakh = 'Ladakh'
    Lakshadweep = 'Lakshadweep'
    Madhya_Pradesh = 'Madhya Pradesh'
    Maharashtra = 'Maharashtra'
    Manipur = 'Manipur'
    Meghalaya = 'Meghalaya'
    Mizoram = 'Mizoram'
    Nagaland = 'Nagaland'
    Odisha = 'Odisha'
    Pondicherry = 'Pondicherry'
    Punjab = 'Punjab'
    Rajasthan = 'Rajasthan'
    Sikkim = 'Sikkim'
    Tamil_Nadu = 'Tamil Nadu'
    Telangana = 'Telangana'
    Tripura = 'Tripura'
    Uttar_Pradesh = 'Uttar Pradesh'
    Uttarakhand = 'Uttarakhand'
    West_Bengal = 'West Bengal'


class StateAndGst:
    data = [
        {'name': StateName.Andaman_Nicobar, 'Gst': GstStateCode.Andaman_and_Nicobar_Islands},
        {'name': StateName.Andhra_Pradesh, 'Gst': GstStateCode.Andhra_Pradesh},
        {'name': StateName.Andhra_Pradesh, 'Gst': GstStateCode.Andhra_Pradesh_new},
        {'name': StateName.Arunachal_Pradesh, 'Gst': GstStateCode.Arunachal_Pradesh},
        {'name': StateName.Assam, 'Gst': GstStateCode.Assam},
        {'name': StateName.Bihar, 'Gst': GstStateCode.Bihar},
        {'name': StateName.Chandigarh, 'Gst': GstStateCode.Chandigarh},
        {'name': StateName.Chattisgarh, 'Gst': GstStateCode.Chattisgarh},
        {'name': StateName.Dadra_Nagar_Haveli_Daman_Diu, 'Gst': GstStateCode.Dadra_and_Nagar_Haveli},
        {'name': StateName.Dadra_Nagar_Haveli_Daman_Diu, 'Gst': GstStateCode.Daman_and_Diu},
        {'name': StateName.Delhi, 'Gst': GstStateCode.Delhi},
        {'name': StateName.Goa, 'Gst': GstStateCode.Goa},
        {'name': StateName.Gujarat, 'Gst': GstStateCode.Gujarat},
        {'name': StateName.Haryana, 'Gst': GstStateCode.Haryana},
        {'name': StateName.Himachal_Pradesh, 'Gst': GstStateCode.Himachal_Pradesh},
        {'name': StateName.Jammu_Kashmir, 'Gst': GstStateCode.Jammu_and_Kashmir},
        {'name': StateName.Jharkhand, 'Gst': GstStateCode.Jharkhand},
        {'name': StateName.Karnataka, 'Gst': GstStateCode.Karnataka},
        {'name': StateName.Kerala, 'Gst': GstStateCode.Kerala},
        {'name': StateName.Ladakh, 'Gst': GstStateCode.Ladakh},
        {'name': StateName.Lakshadweep, 'Gst': GstStateCode.Lakshadweep_Islands},
        {'name': StateName.Madhya_Pradesh, 'Gst': GstStateCode.Madhya_Pradesh},
        {'name': StateName.Maharashtra, 'Gst': GstStateCode.Maharashtra},
        {'name': StateName.Manipur, 'Gst': GstStateCode.Manipur},
        {'name': StateName.Meghalaya, 'Gst': GstStateCode.Meghalaya},
        {'name': StateName.Mizoram, 'Gst': GstStateCode.Mizoram},
        {'name': StateName.Nagaland, 'Gst': GstStateCode.Nagaland},
        {'name': StateName.Odisha, 'Gst': GstStateCode.Odisha},
        {'name': StateName.Pondicherry, 'Gst': GstStateCode.Pondicherry},
        {'name': StateName.Punjab, 'Gst': GstStateCode.Punjab},
        {'name': StateName.Rajasthan, 'Gst': GstStateCode.Rajasthan},
        {'name': StateName.Sikkim, 'Gst': GstStateCode.Sikkim},
        {'name': StateName.Tamil_Nadu, 'Gst': GstStateCode.Tamil_Nadu},
        {'name': StateName.Telangana, 'Gst': GstStateCode.Telangana},
        {'name': StateName.Tripura, 'Gst': GstStateCode.Tripura},
        {'name': StateName.Uttar_Pradesh, 'Gst': GstStateCode.Uttar_Pradesh},
        {'name': StateName.Uttarakhand, 'Gst': GstStateCode.Uttarakhand},
        {'name': StateName.West_Bengal, 'Gst': GstStateCode.West_Bengal},
    ]


def check_state_gst(state, gst):
    flag = False
    for state_code in StateAndGst.data:
        if state_code['name'] == state and state_code['Gst'] == gst:
            flag = True
    return flag
