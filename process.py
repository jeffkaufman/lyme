 # -*- coding: utf-8 -*-

import re

abbr_to_state = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

state_to_abbr = {}
for abbr, state in abbr_to_state.items():
  state_to_abbr[state] = abbr

def age(c_1992_1996, c_1997_2001, c_2002_2006, c_2007_2011):
  weights = [6.0, 7.0, 8.0, 10.0]
  s_weights = sum(weights)
  return (c_1992_1996 * weights[0] +
          c_1997_2001 * weights[1] +
          c_2002_2006 * weights[2] +
          c_2007_2011 * weights[3])/s_weights

colors = "#ffffff #ffffcc #ffeda0 #fed976 #feb24c #fd8d3c #fc4e2a #e31a1c #b10026".split()

def prepare_cutoffs(risks):
  cutoffs = []

  # all non-zeros should vary smoothly from min nonzero risk to max risk in log space

  max_remaining_risk = max(risks)
  for i in range(len(colors)):
    cutoffs.append(max_remaining_risk)
    max_remaining_risk /= 2
  cutoffs.reverse()
  return cutoffs

  #cutoffs.append(0.0001)
  #min_nonzero_risk = cutoffs[0]
  #max_risk = max(risks)
  #step = (max_risk - min_nonzero_risk) / (len(colors) - 1)
  #for i in range(len(colors) - 2):
  #  cutoffs.append(i * step)
  #cutoffs.append(1000000)  # catchall
  #return cutoffs

def determine_color(cutoffs, risk):
  assert len(cutoffs) == len(colors)

  for cutoff, color in zip(cutoffs, colors):
    if risk <= cutoff:
      return color
  assert False  

def start():
  cases = {}
  with open("lyme-by-county.csv") as inf:
    for i, line in enumerate(inf):
      if i == 0:
        continue
      line = line.strip().split(",")
      state = line[2]
      county = line[3]
      
      if state == "Louisiana" and county == "La Salle Parish":
        county = "LaSalle Parish"
      if state == "District of Columbia" and county == "District of Columbia":
        county = "Washington"

      cases["%s, %s" % (county, state)] = [age(*[int(x) if x else 0 for x in line[4:]])]

  with open("PEP_2012_PEPANNRES.csv") as inf:
    for i, line in enumerate(inf):
      if i == 0:
        continue
      line = line.strip()
      county_state = line.split('"')[1]
      if county_state == "District of Columbia, District of Columbia":
        county_state = "Washington, District of Columbia"
      pop2012 = line.split(",")[-1]
      if county_state in cases:
        cases[county_state].append(int(pop2012))

  final_stats = {}
  risks = []
  with open("lyme_risk_by_county.csv", "w") as outf:
    outf.write("county, state, count, 2012 population, annual risk\n")
    for county_state, stats in cases.items():
      if county_state == "Do\xf1a Ana County, New Mexico":
        county_state = "Dona Ana County, New Mexico"

      county, state = county_state.rsplit(", ", 1)
      # unknown county: ignore (mild undercount of risk)
      if county_state == "%s, %s" % (state, state):
        continue

      count, pop = stats

      risks.append(count/pop)

      if count > 0.01:
        outf.write("%s, %s, %s, %.5f%%\n" % (county_state, count, pop, count*100/pop))

      final_stats["%s, %s" % (county, state_to_abbr[state])] = count/pop

  color_cutoffs = prepare_cutoffs(risks)

  path_id_to_text = {}
    
  with open("USA_Counties_with_FIPS_and_names.svg") as inf:
    shapes = inf.read().split("<path")
    new_shapes = []
    
    for shape in shapes:
      match = re.findall('inkscape:label="([^"]*)"', shape)
      if match:
        label = match[0]
        if label.count(",") == 1:
          val = None
          for candidate in [label,
                            label.replace("La Salle, IL", "LaSalle County, IL"),
                            label.replace("La Salle, LA", "LaSalle Parish, LA"),
                            label.replace("Kingsburg, SD", "Kingsbury County, SD"),
                            label.replace("Fairbanks North Stark, AK",
                                          "Fairbanks North Star Borough, AK"),
                            label.replace("Grand Treverse, MI",
                                          "Grand Traverse County, MI"),
                            label.replace("Grand, SD",
                                          "Grant County, SD"),
                            label.replace("Donough, IL",
                                          "McDonough County, IL"),
                            label.replace("Fairfax Co., VA",
                                          "Fairfax city, VA"),
                            label.replace("Guadelupe, NM",
                                          "Guadalupe County, NM"),
                            label.replace("Prince of Wales-Outer Ketchikan, AK",
                                          "Prince of Wales-Hyder Census Area, AK"),
                            label.replace("Worth, NO",
                                          "Worth County, MO"),
                            label.replace("San Franciso, CA",
                                          "San Francisco County, CA"),
                            label.replace("SE Fairbanks, AK",
                                          "Southeast Fairbanks Census Area, AK"),
                            label.replace("McKinely, NM",
                                          "McKinley County, NM"),
                            label.replace("Augusta-Richmond, GA",
                                          "Richmond County, GA"),
                            label.replace("Richmond Co., VA",
                                          "Richmond city, VA"),
                            label.replace("Yukon-Koyukuk, AL",
                                          "Yukon-Koyukuk Census Area, AK"),
                            label.replace("Hartsville-Trousdale, TN",
                                          "Trousdale County, TN"),
                            label.replace("",
                                          ""),
                            label.replace(",", " County,"),
                            label.replace(" Co.,", " County,"),
                            label.replace(",", " city,"),
                            label.replace(" County,", " city,"),
                            label.replace(",", " City and Borough,"),
                            label.replace(",", " City,"),
                            label.replace(",", " Borough,"),
                            label.replace(",", " Census Area,"),
                            label.replace(",", " Municipality,"),
                            label.replace(",", " Parish,")]:
            if val is None and candidate in final_stats:
              val = final_stats[candidate]
              del final_stats[candidate]
              break
          if val is None:
            print "not in final_stats", label
          else:
            color = determine_color(color_cutoffs, val)
            style = ( 
              'font-size:12px;fill-rule:nonzero;stroke:#BBBBBB;stroke-opacity:1;'
              'stroke-width:0.1;stroke-miterlimit:4;stroke-dasharray:none;stroke-linecap:butt;'
              'marker-start:none;stroke-linejoin:bevel;fill:%s' % color)
            shape = re.sub('style="[^"]*"', 'style="%s"' % style, shape)
            path_id = re.findall('id="([^"]*)', shape)[0]
            path_id_to_text[path_id] = "%s: %.4f%%" % (candidate, val*100)
        else:
          shape = shape.replace("#221e1f", "#bbbbbb")  # state lines
      new_shapes.append(shape)
    for remaining_county_state in final_stats:
      print "not on map", remaining_county_state

    popups = []     
    if False:
      for path_id, text in sorted(path_id_to_text.items()):
        #popups.append('<text id="%s-popup" x="250" y="20" font-size="12"'
        #              '      fill="black" visibility="hidden">%s'
        #              '      <set attributeName="visibility" from="hidden" to="visible"'
        #              '           begin="%s.mouseover" end="%s.mouseout"/></text>' % (
        #                path_id, text, path_id, path_id))
        popups.append('<g id="%s-popup" visibility="hidden">'
                      '  <rect x="200" y="5" width="300" height="20"'
                      '        fill="white"></rect>'
                      '  <text x="200" y="16" font-size="12"'
                      '        fill="black">%s</text>'
                      '  <set attributeName="visibility" from="hidden" to="visible"'
                      '       begin="%s.mouseover" end="%s.mouseout"/></g>' % (
                        path_id, text, path_id, path_id))

    svg = "<path".join(new_shapes)
    svg = svg.replace("</svg>", "%s</svg>" % "\n".join(popups))

    with open("out.svg", "w") as outf:
      outf.write(svg)

if __name__ == "__main__":
  start()
