from types import MappingProxyType

from sqlalchemy import REAL, Column, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class EU_Economic_Sentiment(Base):
    __tablename__ = "EU_Economic_Sentiment"
    year = Column(Integer, primary_key=True)
    month = Column(Integer, primary_key=True)
    EU_indu = Column(REAL)
    EU_serv = Column(REAL)
    EU_cons = Column(REAL)
    EU_reta = Column(REAL)
    EU_buil = Column(REAL)
    EU_esi = Column(REAL)
    EU_eei = Column(REAL)
    EA_indu = Column(REAL)
    EA_serv = Column(REAL)
    EA_cons = Column(REAL)
    EA_reta = Column(REAL)
    EA_buil = Column(REAL)
    EA_esi = Column(REAL)
    EA_eei = Column(REAL)
    BE_indu = Column(REAL)
    BE_serv = Column(REAL)
    BE_cons = Column(REAL)
    BE_reta = Column(REAL)
    BE_buil = Column(REAL)
    BE_esi = Column(REAL)
    BE_eei = Column(REAL)
    BG_indu = Column(REAL)
    BG_serv = Column(REAL)
    BG_cons = Column(REAL)
    BG_reta = Column(REAL)
    BG_buil = Column(REAL)
    BG_esi = Column(REAL)
    BG_eei = Column(REAL)
    CZ_indu = Column(REAL)
    CZ_serv = Column(REAL)
    CZ_cons = Column(REAL)
    CZ_reta = Column(REAL)
    CZ_buil = Column(REAL)
    CZ_esi = Column(REAL)
    CZ_eei = Column(REAL)
    DK_indu = Column(REAL)
    DK_serv = Column(REAL)
    DK_cons = Column(REAL)
    DK_reta = Column(REAL)
    DK_buil = Column(REAL)
    DK_esi = Column(REAL)
    DK_eei = Column(REAL)
    DE_indu = Column(REAL)
    DE_serv = Column(REAL)
    DE_cons = Column(REAL)
    DE_reta = Column(REAL)
    DE_buil = Column(REAL)
    DE_esi = Column(REAL)
    DE_eei = Column(REAL)
    EE_indu = Column(REAL)
    EE_serv = Column(REAL)
    EE_cons = Column(REAL)
    EE_reta = Column(REAL)
    EE_buil = Column(REAL)
    EE_esi = Column(REAL)
    EE_eei = Column(REAL)
    IE_indu = Column(REAL)
    IE_serv = Column(REAL)
    IE_cons = Column(REAL)
    IE_reta = Column(REAL)
    IE_buil = Column(REAL)
    IE_esi = Column(REAL)
    IE_eei = Column(REAL)
    EL_indu = Column(REAL)
    EL_serv = Column(REAL)
    EL_cons = Column(REAL)
    EL_reta = Column(REAL)
    EL_buil = Column(REAL)
    EL_esi = Column(REAL)
    EL_eei = Column(REAL)
    ES_indu = Column(REAL)
    ES_serv = Column(REAL)
    ES_cons = Column(REAL)
    ES_reta = Column(REAL)
    ES_buil = Column(REAL)
    ES_esi = Column(REAL)
    ES_eei = Column(REAL)
    FR_indu = Column(REAL)
    FR_serv = Column(REAL)
    FR_cons = Column(REAL)
    FR_reta = Column(REAL)
    FR_buil = Column(REAL)
    FR_esi = Column(REAL)
    FR_eei = Column(REAL)
    HR_indu = Column(REAL)
    HR_serv = Column(REAL)
    HR_cons = Column(REAL)
    HR_reta = Column(REAL)
    HR_buil = Column(REAL)
    HR_esi = Column(REAL)
    HR_eei = Column(REAL)
    IT_indu = Column(REAL)
    IT_serv = Column(REAL)
    IT_cons = Column(REAL)
    IT_reta = Column(REAL)
    IT_buil = Column(REAL)
    IT_esi = Column(REAL)
    IT_eei = Column(REAL)
    CY_indu = Column(REAL)
    CY_serv = Column(REAL)
    CY_cons = Column(REAL)
    CY_reta = Column(REAL)
    CY_buil = Column(REAL)
    CY_esi = Column(REAL)
    CY_eei = Column(REAL)
    LV_indu = Column(REAL)
    LV_serv = Column(REAL)
    LV_cons = Column(REAL)
    LV_reta = Column(REAL)
    LV_buil = Column(REAL)
    LV_esi = Column(REAL)
    LV_eei = Column(REAL)
    LT_indu = Column(REAL)
    LT_serv = Column(REAL)
    LT_cons = Column(REAL)
    LT_reta = Column(REAL)
    LT_buil = Column(REAL)
    LT_esi = Column(REAL)
    LT_eei = Column(REAL)
    LU_indu = Column(REAL)
    LU_serv = Column(REAL)
    LU_cons = Column(REAL)
    LU_reta = Column(REAL)
    LU_buil = Column(REAL)
    LU_esi = Column(REAL)
    LU_eei = Column(REAL)
    HU_indu = Column(REAL)
    HU_serv = Column(REAL)
    HU_cons = Column(REAL)
    HU_reta = Column(REAL)
    HU_buil = Column(REAL)
    HU_esi = Column(REAL)
    HU_eei = Column(REAL)
    MT_indu = Column(REAL)
    MT_serv = Column(REAL)
    MT_cons = Column(REAL)
    MT_reta = Column(REAL)
    MT_buil = Column(REAL)
    MT_esi = Column(REAL)
    MT_eei = Column(REAL)
    NL_indu = Column(REAL)
    NL_serv = Column(REAL)
    NL_cons = Column(REAL)
    NL_reta = Column(REAL)
    NL_buil = Column(REAL)
    NL_esi = Column(REAL)
    NL_eei = Column(REAL)
    AT_indu = Column(REAL)
    AT_serv = Column(REAL)
    AT_cons = Column(REAL)
    AT_reta = Column(REAL)
    AT_buil = Column(REAL)
    AT_esi = Column(REAL)
    AT_eei = Column(REAL)
    PL_indu = Column(REAL)
    PL_serv = Column(REAL)
    PL_cons = Column(REAL)
    PL_reta = Column(REAL)
    PL_buil = Column(REAL)
    PL_esi = Column(REAL)
    PL_eei = Column(REAL)
    PT_indu = Column(REAL)
    PT_serv = Column(REAL)
    PT_cons = Column(REAL)
    PT_reta = Column(REAL)
    PT_buil = Column(REAL)
    PT_esi = Column(REAL)
    PT_eei = Column(REAL)
    RO_indu = Column(REAL)
    RO_serv = Column(REAL)
    RO_cons = Column(REAL)
    RO_reta = Column(REAL)
    RO_buil = Column(REAL)
    RO_esi = Column(REAL)
    RO_eei = Column(REAL)
    SI_indu = Column(REAL)
    SI_serv = Column(REAL)
    SI_cons = Column(REAL)
    SI_reta = Column(REAL)
    SI_buil = Column(REAL)
    SI_esi = Column(REAL)
    SI_eei = Column(REAL)
    SK_indu = Column(REAL)
    SK_serv = Column(REAL)
    SK_cons = Column(REAL)
    SK_reta = Column(REAL)
    SK_buil = Column(REAL)
    SK_esi = Column(REAL)
    SK_eei = Column(REAL)
    FI_indu = Column(REAL)
    FI_serv = Column(REAL)
    FI_cons = Column(REAL)
    FI_reta = Column(REAL)
    FI_buil = Column(REAL)
    FI_esi = Column(REAL)
    FI_eei = Column(REAL)
    SE_indu = Column(REAL)
    SE_serv = Column(REAL)
    SE_cons = Column(REAL)
    SE_reta = Column(REAL)
    SE_buil = Column(REAL)
    SE_esi = Column(REAL)
    SE_eei = Column(REAL)
    UK_indu = Column(REAL)
    UK_serv = Column(REAL)
    UK_cons = Column(REAL)
    UK_reta = Column(REAL)
    UK_buil = Column(REAL)
    UK_esi = Column(REAL)
    UK_eei = Column(REAL)
    ME_indu = Column(REAL)
    ME_serv = Column(REAL)
    ME_cons = Column(REAL)
    ME_reta = Column(REAL)
    ME_buil = Column(REAL)
    ME_esi = Column(REAL)
    ME_eei = Column(REAL)
    MK_indu = Column(REAL)
    MK_serv = Column(REAL)
    MK_cons = Column(REAL)
    MK_reta = Column(REAL)
    MK_buil = Column(REAL)
    MK_esi = Column(REAL)
    MK_eei = Column(REAL)
    AL_indu = Column(REAL)
    AL_serv = Column(REAL)
    AL_cons = Column(REAL)
    AL_reta = Column(REAL)
    AL_buil = Column(REAL)
    AL_esi = Column(REAL)
    AL_eei = Column(REAL)
    RS_indu = Column(REAL)
    RS_serv = Column(REAL)
    RS_cons = Column(REAL)
    RS_reta = Column(REAL)
    RS_buil = Column(REAL)
    RS_esi = Column(REAL)
    RS_eei = Column(REAL)
    TR_indu = Column(REAL)
    TR_serv = Column(REAL)
    TR_cons = Column(REAL)
    TR_reta = Column(REAL)
    TR_buil = Column(REAL)
    TR_esi = Column(REAL)
    TR_eei = Column(REAL)

    @classmethod
    def name(cls):
        return cls.__tablename__

    @classmethod
    def columns(cls):
        return [c.name for c in cls.__table__.columns]

    @staticmethod
    def column_map():
        return MappingProxyType(
            {
                "Year": "year",
                "Month": "month",
                "EU.INDU": "EU_indu",
                "EU.SERV": "EU_serv",
                "EU.CONS": "EU_cons",
                "EU.RETA": "EU_reta",
                "EU.BUIL": "EU_buil",
                "EU.ESI": "EU_esi",
                "EU.EEI": "EU_eei",
                "EA.INDU": "EA_indu",
                "EA.SERV": "EA_serv",
                "EA.CONS": "EA_cons",
                "EA.RETA": "EA_reta",
                "EA.BUIL": "EA_buil",
                "EA.ESI": "EA_esi",
                "EA.EEI": "EA_eei",
                "BE.INDU": "BE_indu",
                "BE.SERV": "BE_serv",
                "BE.CONS": "BE_cons",
                "BE.RETA": "BE_reta",
                "BE.BUIL": "BE_buil",
                "BE.ESI": "BE_esi",
                "BE.EEI": "BE_eei",
                "BG.INDU": "BG_indu",
                "BG.SERV": "BG_serv",
                "BG.CONS": "BG_cons",
                "BG.RETA": "BG_reta",
                "BG.BUIL": "BG_buil",
                "BG.ESI": "BG_esi",
                "BG.EEI": "BG_eei",
                "CZ.INDU": "CZ_indu",
                "CZ.SERV": "CZ_serv",
                "CZ.CONS": "CZ_cons",
                "CZ.RETA": "CZ_reta",
                "CZ.BUIL": "CZ_buil",
                "CZ.ESI": "CZ_esi",
                "CZ.EEI": "CZ_eei",
                "DK.INDU": "DK_indu",
                "DK.SERV": "DK_serv",
                "DK.CONS": "DK_cons",
                "DK.RETA": "DK_reta",
                "DK.BUIL": "DK_buil",
                "DK.ESI": "DK_esi",
                "DK.EEI": "DK_eei",
                "DE.INDU": "DE_indu",
                "DE.SERV": "DE_serv",
                "DE.CONS": "DE_cons",
                "DE.RETA": "DE_reta",
                "DE.BUIL": "DE_buil",
                "DE.ESI": "DE_esi",
                "DE.EEI": "DE_eei",
                "EE.INDU": "EE_indu",
                "EE.SERV": "EE_serv",
                "EE.CONS": "EE_cons",
                "EE.RETA": "EE_reta",
                "EE.BUIL": "EE_buil",
                "EE.ESI": "EE_esi",
                "EE.EEI": "EE_eei",
                "IE.INDU": "IE_indu",
                "IE.SERV": "IE_serv",
                "IE.CONS": "IE_cons",
                "IE.RETA": "IE_reta",
                "IE.BUIL": "IE_buil",
                "IE.ESI": "IE_esi",
                "IE.EEI": "IE_eei",
                "EL.INDU": "EL_indu",
                "EL.SERV": "EL_serv",
                "EL.CONS": "EL_cons",
                "EL.RETA": "EL_reta",
                "EL.BUIL": "EL_buil",
                "EL.ESI": "EL_esi",
                "EL.EEI": "EL_eei",
                "ES.INDU": "ES_indu",
                "ES.SERV": "ES_serv",
                "ES.CONS": "ES_cons",
                "ES.RETA": "ES_reta",
                "ES.BUIL": "ES_buil",
                "ES.ESI": "ES_esi",
                "ES.EEI": "ES_eei",
                "FR.INDU": "FR_indu",
                "FR.SERV": "FR_serv",
                "FR.CONS": "FR_cons",
                "FR.RETA": "FR_reta",
                "FR.BUIL": "FR_buil",
                "FR.ESI": "FR_esi",
                "FR.EEI": "FR_eei",
                "HR.INDU": "HR_indu",
                "HR.SERV": "HR_serv",
                "HR.CONS": "HR_cons",
                "HR.RETA": "HR_reta",
                "HR.BUIL": "HR_buil",
                "HR.ESI": "HR_esi",
                "HR.EEI": "HR_eei",
                "IT.INDU": "IT_indu",
                "IT.SERV": "IT_serv",
                "IT.CONS": "IT_cons",
                "IT.RETA": "IT_reta",
                "IT.BUIL": "IT_buil",
                "IT.ESI": "IT_esi",
                "IT.EEI": "IT_eei",
                "CY.INDU": "CY_indu",
                "CY.SERV": "CY_serv",
                "CY.CONS": "CY_cons",
                "CY.RETA": "CY_reta",
                "CY.BUIL": "CY_buil",
                "CY.ESI": "CY_esi",
                "CY.EEI": "CY_eei",
                "LV.INDU": "LV_indu",
                "LV.SERV": "LV_serv",
                "LV.CONS": "LV_cons",
                "LV.RETA": "LV_reta",
                "LV.BUIL": "LV_buil",
                "LV.ESI": "LV_esi",
                "LV.EEI": "LV_eei",
                "LT.INDU": "LT_indu",
                "LT.SERV": "LT_serv",
                "LT.CONS": "LT_cons",
                "LT.RETA": "LT_reta",
                "LT.BUIL": "LT_buil",
                "LT.ESI": "LT_esi",
                "LT.EEI": "LT_eei",
                "LU.INDU": "LU_indu",
                "LU.SERV": "LU_serv",
                "LU.CONS": "LU_cons",
                "LU.RETA": "LU_reta",
                "LU.BUIL": "LU_buil",
                "LU.ESI": "LU_esi",
                "LU.EEI": "LU_eei",
                "HU.INDU": "HU_indu",
                "HU.SERV": "HU_serv",
                "HU.CONS": "HU_cons",
                "HU.RETA": "HU_reta",
                "HU.BUIL": "HU_buil",
                "HU.ESI": "HU_esi",
                "HU.EEI": "HU_eei",
                "MT.INDU": "MT_indu",
                "MT.SERV": "MT_serv",
                "MT.CONS": "MT_cons",
                "MT.RETA": "MT_reta",
                "MT.BUIL": "MT_buil",
                "MT.ESI": "MT_esi",
                "MT.EEI": "MT_eei",
                "NL.INDU": "NL_indu",
                "NL.SERV": "NL_serv",
                "NL.CONS": "NL_cons",
                "NL.RETA": "NL_reta",
                "NL.BUIL": "NL_buil",
                "NL.ESI": "NL_esi",
                "NL.EEI": "NL_eei",
                "AT.INDU": "AT_indu",
                "AT.SERV": "AT_serv",
                "AT.CONS": "AT_cons",
                "AT.RETA": "AT_reta",
                "AT.BUIL": "AT_buil",
                "AT.ESI": "AT_esi",
                "AT.EEI": "AT_eei",
                "PL.INDU": "PL_indu",
                "PL.SERV": "PL_serv",
                "PL.CONS": "PL_cons",
                "PL.RETA": "PL_reta",
                "PL.BUIL": "PL_buil",
                "PL.ESI": "PL_esi",
                "PL.EEI": "PL_eei",
                "PT.INDU": "PT_indu",
                "PT.SERV": "PT_serv",
                "PT.CONS": "PT_cons",
                "PT.RETA": "PT_reta",
                "PT.BUIL": "PT_buil",
                "PT.ESI": "PT_esi",
                "PT.EEI": "PT_eei",
                "RO.INDU": "RO_indu",
                "RO.SERV": "RO_serv",
                "RO.CONS": "RO_cons",
                "RO.RETA": "RO_reta",
                "RO.BUIL": "RO_buil",
                "RO.ESI": "RO_esi",
                "RO.EEI": "RO_eei",
                "SI.INDU": "SI_indu",
                "SI.SERV": "SI_serv",
                "SI.CONS": "SI_cons",
                "SI.RETA": "SI_reta",
                "SI.BUIL": "SI_buil",
                "SI.ESI": "SI_esi",
                "SI.EEI": "SI_eei",
                "SK.INDU": "SK_indu",
                "SK.SERV": "SK_serv",
                "SK.CONS": "SK_cons",
                "SK.RETA": "SK_reta",
                "SK.BUIL": "SK_buil",
                "SK.ESI": "SK_esi",
                "SK.EEI": "SK_eei",
                "FI.INDU": "FI_indu",
                "FI.SERV": "FI_serv",
                "FI.CONS": "FI_cons",
                "FI.RETA": "FI_reta",
                "FI.BUIL": "FI_buil",
                "FI.ESI": "FI_esi",
                "FI.EEI": "FI_eei",
                "SE.INDU": "SE_indu",
                "SE.SERV": "SE_serv",
                "SE.CONS": "SE_cons",
                "SE.RETA": "SE_reta",
                "SE.BUIL": "SE_buil",
                "SE.ESI": "SE_esi",
                "SE.EEI": "SE_eei",
                "UK.INDU": "UK_indu",
                "UK.SERV": "UK_serv",
                "UK.CONS": "UK_cons",
                "UK.RETA": "UK_reta",
                "UK.BUIL": "UK_buil",
                "UK.ESI": "UK_esi",
                "UK.EEI": "UK_eei",
                "ME.INDU": "ME_indu",
                "ME.SERV": "ME_serv",
                "ME.CONS": "ME_cons",
                "ME.RETA": "ME_reta",
                "ME.BUIL": "ME_buil",
                "ME.ESI": "ME_esi",
                "ME.EEI": "ME_eei",
                "MK.INDU": "MK_indu",
                "MK.SERV": "MK_serv",
                "MK.CONS": "MK_cons",
                "MK.RETA": "MK_reta",
                "MK.BUIL": "MK_buil",
                "MK.ESI": "MK_esi",
                "MK.EEI": "MK_eei",
                "AL.INDU": "AL_indu",
                "AL.SERV": "AL_serv",
                "AL.CONS": "AL_cons",
                "AL.RETA": "AL_reta",
                "AL.BUIL": "AL_buil",
                "AL.ESI": "AL_esi",
                "AL.EEI": "AL_eei",
                "RS.INDU": "RS_indu",
                "RS.SERV": "RS_serv",
                "RS.CONS": "RS_cons",
                "RS.RETA": "RS_reta",
                "RS.BUIL": "RS_buil",
                "RS.ESI": "RS_esi",
                "RS.EEI": "RS_eei",
                "TR.INDU": "TR_indu",
                "TR.SERV": "TR_serv",
                "TR.CONS": "TR_cons",
                "TR.RETA": "TR_reta",
                "TR.BUIL": "TR_buil",
                "TR.ESI": "TR_esi",
                "TR.EEI": "TR_eei",
            }
        )
