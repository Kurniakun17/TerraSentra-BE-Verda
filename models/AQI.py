def calculate_aqi_ispu(pm25):
    rentang_pm25 = [
        (0.0, 15.5, 0, 50),
        (15.6, 55.4, 51, 100),
        (55.5, 150.4, 101, 199),
        (150.5, 250.4, 200, 299),
        (250.5, 500.4, 300, 500),
    ]
    
    for bp_low, bp_high, aqi_low, aqi_high in rentang_pm25:
        if bp_low <= pm25 <= bp_high:
            return round(((aqi_high - aqi_low) / (bp_high - bp_low)) * (pm25 - bp_low) + aqi_low)
    return None  
