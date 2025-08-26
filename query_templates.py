query_templates = {
    "1": {  # Leave Info
        "1": "SELECT SUM(SICK_LEAVE) AS SICK_LEAVE FROM full_data WHERE {where}",
        "2": "SELECT SUM(ABSENT) AS ABSENT FROM full_data WHERE {where}",
        "3": "SELECT SUM(OTHER_NON_LEAVE) AS OTHER_NON_LEAVE FROM full_data WHERE {where}",
        "4": "SELECT SUM(LEAVE_DAYS) AS LEAVE_DAYS FROM full_data WHERE {where}",
        "5": "SELECT SUM(SICK_LEAVE + OTHER_NON_LEAVE + LEAVE_DAYS + ABSENT) AS TOTAL_LEAVE FROM full_data WHERE {where}"
    },

    "2": {  # Duty Info
        "1": "SELECT SUM(TOTAL_DUTY) AS TOTAL_DUTY FROM full_data WHERE {where}",
        "2": "SELECT SUM(RUN_DUTY_MIN) AS RUN_DUTY FROM full_data WHERE {where}",
        "3": "SELECT SUM(NON_RUN_DUTY_MIN) AS NON_RUN_DUTY FROM full_data WHERE {where}",
        "4": "SELECT SUM(STATIONAY_DUTY) AS STATIONARY_DUTY FROM full_data WHERE {where}",
        "5": "SELECT SUM(SPARE_DUTY_MINS_N) AS SPARE_DUTY_MINS, SUM(SPARE_KMS_N) AS SPARE_KMS FROM full_data WHERE {where}",
        "6": "SELECT SUM(BOR) AS BREACH_OF_REST FROM full_data WHERE {where}",
        "7": "SELECT SUM(NGHT) AS NIGHT_DUTY FROM full_data WHERE {where}",
        "8": "SELECT SUM(TEST_TRNG) AS TEST_TRAINING FROM full_data WHERE {where}",
        "9": "SELECT SUM(RRA) AS RRA FROM full_data WHERE {where}",
        "10": "SELECT DISTINCT TENTATIVE_FLAG FROM full_data WHERE CREW_ID_V = :crew_id",
        "11": "SELECT SUM(SHUNT_COUNT) AS SHUNTING_DUTY_COUNT FROM full_data WHERE {where}"
    },

    "3": {  # KMs Summary
        "1": "SELECT SUM(TOTAL_KMS) AS TOTAL_KMS FROM full_data WHERE {where}",
        "2": "SELECT SUM(FOOT_PLT_KM) AS FOOTPLATE_KMS FROM full_data WHERE {where}",
        "3": "SELECT SUM(TOTAL_KMS - COALESCE(FOOT_PLT_KM, 0)) AS FREIGHT_KMS FROM full_data WHERE {where}",
        "4": "SELECT SUM(NRDA_KMS) AS NRDA_KMS FROM full_data WHERE {where}",
        "5": "SELECT SUM(OSRA_KMS) AS OSRA_KMS FROM full_data WHERE {where}",
        "6": "SELECT SUM(COACH_FOOT_PLT_KM_N) AS COACH_KM, SUM(COACH_RUN_DUTY_MIN_N) AS COACH_MIN FROM full_data WHERE {where}",
        "7": "SELECT SUM(OFF1_KMS + OFF2_KMS) AS OFF_DUTY_KMS FROM full_data WHERE {where}",
        "8": "SELECT SUM(ALKM_NON_LEAVE) AS AUTH_LEAVE_KMS FROM full_data WHERE {where}",
        "9": "SELECT SUM(ALKM_LEAVE) AS ALKM_LEAVE_KMS FROM full_data WHERE {where}"
    },

    "4": {  # Trip Info
        "1": "SELECT SUM(NO_OF_TRIPS_N) AS NO_OF_TRIPS FROM full_data WHERE {where}",
        "2": "SELECT SUM(TRIP_COUNT) AS TRIP_COUNT FROM full_data WHERE {where}"
    },

    "5": {  # Crew Info
        "1": "SELECT NAME_V, CREW_CADRE_V, CREW_DESIG_V, MOBILE_NO_N, HQ_CODE_C FROM full_data WHERE CREW_ID_V = :crew_id LIMIT 1",
        "2": "SELECT AU_CODE_V, PF_CODE_N, LI_ID_V FROM full_data WHERE CREW_ID_V = :crew_id LIMIT 1",
        "3": "SELECT ORG_TYPE_C, TRCTN_C, IPAS_FLAG_C, ALCOHOL_C, FLAG_C FROM full_data WHERE CREW_ID_V = :crew_id LIMIT 1",
        "4": "SELECT INACTIVE_STTS_V, INACTIVE_RESN_V FROM full_data WHERE CREW_ID_V = :crew_id LIMIT 1",
        "5": "SELECT VALID_FROM_DATETIME_D, VALID_TO_DATETIME_D FROM full_data WHERE CREW_ID_V = :crew_id LIMIT 1",
        "6": "SELECT EMP_NO_V, CREW_BASE_ID_V FROM full_data WHERE CREW_ID_V = :crew_id LIMIT 1"
    },

    "6": {  # Location & Time Info
        "1": "SELECT HQ_CODE_C, SUM(TOTAL_DUTY) AS DUTY, SUM(TOTAL_KMS) AS KMS FROM full_data WHERE {where} GROUP BY HQ_CODE_C",
        "2": "SELECT STRFTIME('%Y-%m', DATE_TIME_D) AS MONTH, SUM(TOTAL_DUTY) AS TOTAL_DUTY, SUM(TOTAL_KMS) AS TOTAL_KMS, SUM(NO_OF_TRIPS_N) AS TOTAL_TRIPS FROM full_data WHERE CREW_ID_V = :crew_id GROUP BY MONTH ORDER BY MONTH",
        "3": "SELECT NH_DATES, SUM(NH) AS NH_COUNT FROM full_data WHERE {where} GROUP BY NH_DATES",
        "4": "SELECT DISTINCT SLOT_NUMBER_N, MONTH_HRS_FROM_DATE_D, MONTH_HRS_TO_DATE_D FROM full_data WHERE CREW_ID_V = :crew_id"
    }
}
