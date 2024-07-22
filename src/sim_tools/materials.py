import dataclasses


@dataclasses.dataclass
class MaterialOptical:
    """Absorption coefficient"""

    epsilon: float
    """Reflectivity"""
    R: float
    """Thermal conductivity"""
    k: float
    """Density"""
    rho: float
    """Heat capacity at constant pressure"""
    Cp: float


"""Typical borosilicate glass"""
BoroSilicate = MaterialOptical(epsilon=0.8, R=0.08, k=1.2, rho=2230, Cp=830)

"""Typical fused quartz glass"""
FusedSilica = MaterialOptical(epsilon=0.93, R=0.05, k=1.2, rho=2230, Cp=830)

"""SCHOTT NBK-7 glass"""
NBK7 = MaterialOptical(epsilon=0.7, R=0.16, k=1.114, rho=2510, Cp=858)
