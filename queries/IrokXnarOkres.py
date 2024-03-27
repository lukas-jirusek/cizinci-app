from oblasti import oblasti
from narodnosti import narodnosti

import pandas as pd


def IrokXnarOkres(data, cur):
    params = data["parameters"]


    # soucet 
    query = f"""SELECT 
        SUM(hodnota) AS total_foreigners
    FROM 
        zaznam_denormalised
    WHERE 
        rok = '{params["end_year"]}' AND  
        okres_kod = '{params["area_kod"]}';
    """
    cur.execute(query)
    current = cur.fetchall()[0][0]
    
    if params["end_year"] != "2004":
        # soucet 
        query = f"""SELECT 
            SUM(hodnota) AS total_foreigners
        FROM 
            zaznam_denormalised
        WHERE 
            rok = '{int(params["end_year"]) - 1}' AND  
            okres_kod = '{params["area_kod"]}';
        """
        cur.execute(query)
        prev = cur.fetchall()[0][0]
        if current > prev:
            change = f"+ {current - prev}"
        else:
            change = f"- {prev - current}"
    else:
        prev = False
        change = False
    
    data["totalCount"]["current"] = current
    data["totalCount"]["last"] = prev
    data["totalCount"]["change"] = change

    # vekova
    ageQuery = f"""SELECT 
        SUM(hodnota) AS total_foreigners
    FROM 
        zaznam_denormalised
    WHERE 
        rok = '{params["end_year"]}' AND  
        okres_kod = '{params["area_kod"]}'
    GROUP BY 
        vek_kod
    ORDER BY 
        vek_kod;
    """

    cur.execute(ageQuery)
    result = cur.fetchall()
    data["ageChart"]["values"] = [x[0] for x in result]

    # pohlavi
    genderQuery = f"""SELECT 
        SUM(hodnota) AS total_foreigners
    FROM 
        zaznam_denormalised
    WHERE 
        rok = '{params["end_year"]}' AND  
        okres_kod = '{params["area_kod"]}'
    GROUP BY 
        pohlavi_kod
    ORDER BY 
        pohlavi_kod;
    """

    cur.execute(genderQuery)
    result = cur.fetchall()
    data["pieData"]["values"] = [x[0] for x in result]
    
    # vyvoj
    data["chartData"]["display"] = False

    # areas / year
    data["subregionYearTable"]["display"] = False

    # narodnost / rok
    query = f"""
    SELECT 
        rok AS year, 
        obcanstvi_kod, 
        SUM(hodnota) AS total_foreigners
    FROM 
        zaznam_denormalised
    WHERE 
        rok = '{params["end_year"]}' AND
        okres_kod = '{params["area_kod"]}'
    GROUP BY 
        rok, obcanstvi_kod
    ORDER BY 
        rok, obcanstvi_kod;
    """
    cur.execute(query)
    subregions = cur.fetchall()
    
    subregions = sorted([(x[0], narodnosti[x[1]], x[2]) for x in subregions], key=lambda x: x[1])
    
    df = pd.DataFrame(subregions, columns=['Year', 'Nationality', 'Count'])
    
    pivot_table = df.pivot(index='Nationality', columns='Year', values='Count').fillna(0).convert_dtypes(convert_integer=True)
    pivot_table = pivot_table.sort_values(by=pivot_table.columns[-1], ascending=False)
    
    headers = pivot_table.columns.tolist()
    index = pivot_table.index.tolist()
    values = pivot_table.values.tolist()
    
    
    data["nationalityYearTable"]["display"] = True
    data["nationalityYearTable"]["headers"] = headers
    data["nationalityYearTable"]["first_col"] = index
    data["nationalityYearTable"]["data"] = values
