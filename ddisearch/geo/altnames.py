# alternate names, e.g. for historic places

# dictionary of placenames that should be looked up or geocoded
# as a different value

alternate_names = {
    # Palestinian Territory
    'Palestine': 'Palestinian Territory',
    'West Bank and Gaza Strip': 'Palestinian Territory',
    'West Bank And Gaza Strip': 'Palestinian Territory',
    'West Bank and Gaza': 'Palestinian Territory',
    'West Bank And Gaza': 'Palestinian Territory',
    # Venezuela
    'Venezuela, RB': 'Venezuela',
    # USSR now handled separately (added old country code to geonames data)
    # 'Soviet Union': 'Russia',
    # DRC
    'Zaire': 'Democratic Republic of the Congo',
    # The Vietnams, Past and Present
    'South Vietnam': 'Vietnam',
    'Vietnam Republic': 'Vietnam',
    'North Vietnam': 'Vietnam',
    "Vietnam People's Rep": 'Vietnam',
    # map historic german states to Germany proper because there are
    # no contemporary equivalents close enough to be accurate
    'Hesse, Electorate': 'Germany',
    'Hesse, Grand Duchy': 'Germany',
    'Baden': 'Germany',
    'Bavaria': 'Germany',
    'Hanover': 'Germany',
    'Mecklenburg': 'Germany',
    'Prussia': 'Germany',
    'Saxony': 'Germany',
    'Wurttemberg': 'Germany',
    # code pre-unification Italian states at the country level as well
    'Modena': 'Italy',
    'Papal States': 'Italy',
    'Parma': 'Italy',
    'Sardinia': 'Italy',
    'Two Sicilies': 'Italy',
    'Tuscany': 'Italy',
    # map variant names of the Habsburg Empire to current-day Austria
    'Austria-Hungary': 'Austria',
    'Austrian Empire': 'Austria',
    # map East Germany and variants thereof to Germany
    'German Democratic Republic': 'Germany',
    'East Germany': 'Germany',
    # map West Germany and variants thereof to Germany
    'Federal Republic of Germany': 'Germany',
    'West Germany': 'Germany',
    # Bahamas
    'Bahamas, The': 'Bahamas',
    # Bahrain
    'Bahrain, Kingdom of': 'Bahrain',
    # Bosnia-Herzegovina
    'Bosnia': 'Bosnia and Herzegovina',
    'Bosnia-Herzegovina': 'Bosnia and Herzegovina',
    'Bosnia-Hercegovina': 'Bosnia and Herzegovina',
    # Brunei
    'Brunei Darussalam': 'Brunei',
    # Burma/Myanmar
    'Burma': 'Myanmar',
    # Cape Verde
    'Cabo Verde': 'Cape Verde',
    # Comoros/Comoro Islands
    'Comoro Islands': 'Comoros',
    'Anjouan': 'Comoros',
    # Ivory Coast
    "Cote D'Ivoire": 'Ivory Coast',
    "Cote d'Ivoire": 'Ivory Coast',
    # Egypt
    'Egypt, Arab Rep.': 'Egypt',
    # Faroe Islands
    'Faeroe Islands': 'Faroe Islands',
    # Gambia
    'Gambia, The': 'Gambia',
    # Guinea-Bissau
    'Guinea Bissau': 'Guinea-Bissau',
    # The Vatican
    'Holy See (Vatican City)': 'Vatican',
    # Kyrgyzstan
    'Kyrgyz Republic': 'Kyrgyzstan',
    # Macedonia
    'Macedonia, FYR': 'Macedonia',
    # Micronesia
    'Micronesia, Fed. Sts.': 'Micronesia',
    # Republic of the Congo
    'Republic of Congo': 'Republic of the Congo',
    # Saint Kitts and Nevis
    'St. Kitts And Nevis': 'Saint Kitts and Nevis',
    'St. Kitts and Nevis': 'Saint Kitts and Nevis',
    # Saint Lucia
    'St. Lucia': 'Saint Lucia',
    # Saint Martin (French)
    'St. Martin (French part)': 'Saint Martin',
    # Saint Vincent and the Grenadines
    'St. Vincent And The Grenadines': 'Saint Vincent and the Grenadines',
    'St. Vincent and the Grenadines': 'Saint Vincent and the Grenadines',
    # Slovakia
    'Slovak Republic': 'Slovakia',
    # USSR
    'Soviet Union': 'Union of Soviet Socialist Republics',
    'USSR': 'Union of Soviet Socialist Republics',
    # Syria
    'Syrian Arab Republic': 'Syria',
    # East Timor
    'Timor-Leste': 'East Timor',
    # Virgin Islands
    'Virgin Islands': 'U.S. Virgin Islands',
    # Cyprus
    'Cyprus, Greek': 'Cyprus',
    'Cyprus, Turkey': 'Cyprus',
    # Somaliland
    'Somaliland': 'Somalia',
    # The Yemens
    'Yemen Arab Republic': 'Yemen',
    'North Yemen': 'Yemen',
    "Yemen People's Democratic Republic": 'Yemen',
    "South Yemen": 'Yemen',
    # Tanzania
    'Zanzibar': 'Tanzania',

    # The following entities will be not be geocoded for various reasons:
    # - hardly any data sources will have coverage of them
    # - they won't show up on any map
    # - they are not sovereign states
    #
    # Bophuthatswana - wouldn't show up in any map, and I don't feel the need to
    #   suggest any legitimacy for relics of apartheid
    # Channel Islands
    # Ciskei - another South African Bantustan
    # Jersey, Channel Islands
    # Netherlands Antilles
    # Netherlands Antilles (Former)
    # Senegambia - a short-lived union between Senegal and the Gambia
    # Transkei - another South African Bantustan
    # Venda - another South African Bantustan
}

