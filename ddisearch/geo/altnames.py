# alternate names, e.g. for historic places

# dictionary of placenames that should be looked up or geocoded
# as a different value

alternate_names = {
    'Palestine': 'Palestinian Territory',
    'West Bank and Gaza Strip': 'Palestinian Territory',
    # Venezuela
    'Venezuela, RB': 'Venezuela',
    # USSR now handled separately (added old country code to geonames data)
    # 'Soviet Union': 'Russia',
    'Zaire': 'Democratic Republic of the Congo',
    'South Vietnam': 'Vietnam',
    'North Vietnam': 'Vietnam',
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
}

