class VendorErrorConstants:
    # activity detail
    DETAILNAME = 'DETAILNAME CANNOT BE NULL'
    RAISOR = 'RAISOR CANNOT BE NULL'
    APPROVER = 'APPROVER CANNOT BE NULL'
    # catalog
    ACTIVITYDETAIL = 'ACTIVITYDETAIL ID CANNOT BE NULL'
    PRODUCTNAME = 'PRODUCTNAME CANNOT BE NULL'
    CATEGORY = 'CATEGORY CANNOT BE NULL'
    SUBCATEGORY = 'SUBCATEGORY CANNOT BE NULL'
    UOM = 'UOM CANNOT BE NULL'
    UNITPRICE = 'UNIT PRICE CANNOT BE NULL'
    DATEFROM = 'FROM DATE CANNOT BE NULL'
    DATETO = 'TO DATE CANNOT BE NULL'
    # activity
    NAME = 'NAME CANNOT BE NULL'
    TYPE = 'TYPE CANNOT BE NULL'
    START_DATE = 'START DATE CANNOT BE NULL'
    END_DATE = 'END DATE CANNOT BE NULL'
    RM = 'RM CANNOT BE NULL'
    ACTIVITY_STATUS = 'ACTIVITY STATUS CANNOT BE NULL'
    # contact
    DESIGNATION = 'DESIGNATION CANNOT BE NULL'
    MOBILE = 'MOBILE CANNOT BE NULL'
    # address
    LINE_1 = 'LINE 1 CANNOT BE NULL'
    PINCODE_ID = 'PINCODE ID CANNOT BE NULL'
    CITY_ID = 'CITY ID CANNOT BE NULL'
    DISTRICT_ID = 'DISTRICT ID CANNOT BE NULL'
    STATE_ID = 'STATE ID CANNOT BE NULL'
    # suppliertax
    TAX = 'TAX CANNOT BE NULL'
    SUBTAX = 'SUBTAX CANNOT BE NULL'
    PAN_NO = 'PAN NUMBER CANNOT BE NULL'
    EXCEM_FROM = 'EXCEM FROM CANNOT BE NULL'
    EXCEM_TO = 'EXCEM TO CANNOT BE NULL'
    EXCEM_THROSOLD = 'EXCEM THROSOLD CANNOT BE NULL'
    EXCEM_RATE = 'EXCEM RATE CANNOT BE NULL'
    TAX_RATE = 'TAX RATE CANNOT BE NULL'
    # vendor


class VendorMandatory:
    def activity_detail(self, obj):
        check = True
        response = None
        # if (obj.get_detailname() is None) or (obj.get_detailname() == ""):
        #     check = False
        #     response = VendorErrorConstants.DETAILNAME
        if (obj.get_raisor() is None) or (obj.get_raisor() == ""):
            check = False
            response = VendorErrorConstants.RAISOR
        elif (obj.get_approver() is None) or (obj.get_approver() == ""):
            check = False
            response = VendorErrorConstants.APPROVER
        result = {"checker": check, "response": response}
        return result

    def catalog(self,obj):
        check = True
        response = None
        if (obj.get_product_name() is None) or (obj.get_product_name() == ""):
            check = False
            response = VendorErrorConstants.PRODUCTNAME
        elif (obj.get_category() is None) or (obj.get_category() == ""):
            check = False
            response = VendorErrorConstants.CATEGORY
        elif (obj.get_subcategory() is None) or (obj.get_subcategory() == ""):
            check = False
            response = VendorErrorConstants.SUBCATEGORY
        # elif (obj.get_uom() is None) or (obj.get_uom() == ""):
        #     check = False
        #     response = VendorErrorConstants.UOM
        # elif (obj.get_unitprice() is None) or (obj.get_unitprice() == ""):
        #     check = False
        #     response = VendorErrorConstants.UNITPRICE
        # elif (obj.get_from_date() is None) or (obj.get_from_date() == ""):
        #     check = False
        #     response = VendorErrorConstants.DATEFROM
        # elif (obj.get_to_date() is None) or (obj.get_to_date() == ""):
        #     check = False
        #     response = VendorErrorConstants.DATETO
        result = {"checker": check, "response": response}
        return result

    def activity(self, obj,):
        check = True
        response = None

        # if (obj.get_name() is None) or (obj.get_name() == ""):
        #     check = False
        #     response = VendorErrorConstants.NAME
        if (obj.get_type() is None) or (obj.get_type() == ""):
            check = False
            response = VendorErrorConstants.TYPE
        elif (obj.get_rm() is None) or (obj.get_rm() == ""):
            check = False
            response = VendorErrorConstants.RM
        elif (obj.get_activity_status() is None) or (obj.get_activity_status() == ""):
            check = False
            response = VendorErrorConstants.ACTIVITY_STATUS
        result = {"checker": check, "response": response}
        return result

    def contact(self, obj):
        check = True
        response = None
        # if (obj.get_name() is None) or (obj.get_name() == ""):
        #     check = False
        #     response = VendorErrorConstants.NAME
        # elif (obj.get_designation() is None) or (obj.get_designation() == ""):
        #     check = False
        #     response = VendorErrorConstants.DESIGNATION
        result = {"checker": check, "response": response}
        return result

    def address(self, obj):
        check = True
        response = None
        if (obj.get_line1() is None) or (obj.get_line1() == ""):
            check = False
            response = VendorErrorConstants.LINE_1
        elif (obj.get_pincode_id() is None) or (obj.get_pincode_id() == ""):
            check = False
            response = VendorErrorConstants.PINCODE_ID
        elif (obj.get_city_id() is None) or (obj.get_city_id() == ""):
            check = False
            response = VendorErrorConstants.CITY_ID
        elif (obj.get_district_id() is None) or (obj.get_district_id() == ""):
            check = False
            response = VendorErrorConstants.DISTRICT_ID
        elif (obj.get_state_id() is None) or (obj.get_state_id() == ""):
            check = False
            response = VendorErrorConstants.STATE_ID
        result = {"checker": check, "response": response}
        return result

    def branch(self, obj):
        check = True
        response = None
        if (obj.get_name() is None) or (obj.get_name() == ""):
            check = False
            response = VendorErrorConstants.NAME
        result = {"checker": check, "response": response}
        return result

    def suppliertax(self, obj):
        check = True
        response = None
        # if (obj.get_isexcempted() == True):
        #     if (obj.get_excemfrom() is None) or (obj.get_excemfrom() == ""):
        #         check = False
        #         response = VendorErrorConstants.EXCEM_FROM
        #     elif (obj.get_excemto() is None) or (obj.get_excemto() == ""):
        #         check = False
        #         response = VendorErrorConstants.EXCEM_TO
        #     elif (obj.get_excemthrosold() is None) or (obj.get_excemthrosold() == ""):
        #         check = False
        #         response = VendorErrorConstants.EXCEM_THROSOLD
        #     elif (obj.get_excemrate() is None) or (obj.get_excemrate() == ""):
        #         check = False
        #         response = VendorErrorConstants.EXCEM_RATE
        if (obj.get_tax() is None) or (obj.get_tax() == ""):
            check = False
            response = VendorErrorConstants.TAX
        elif (obj.get_subtax() is None) or (obj.get_subtax() == ""):
            check = False
            response = VendorErrorConstants.SUBTAX
        elif (obj.get_taxrate() is None) or (obj.get_taxrate() == ""):
            check = False
            response = VendorErrorConstants.TAX_RATE
        result = {"checker": check, "response": response}
        return result

    def vendor(self):
        check = True
        response = None
        result = {"checker": check, "response": response}
        return result
