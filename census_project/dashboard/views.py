from django.shortcuts import render
from django.db.models import Sum
from .models import PopulationData
import json

# Unified container class to represent dashboard metrics for any scope
class DashboardData:
    def __init__(self, persons, population, annual_growth_rate,
                 males_2001, females_2001, male_2011, female_2011,
                 persons_literate_2001,
                 age_0_4_2001, age_5_14_2001, age_15_59_2001, age_60_plus_2001,
                 age_0_29_2011, age_30_49_2011, age_50_2011,
                 pop_years_dict):
        self.persons = int(persons)
        self.population = int(population)
        self.annual_growth_rate = float(annual_growth_rate)
        
        # Gender counts
        self.males_2001 = int(males_2001)
        self.females_2001 = int(females_2001)
        self.male_2011 = int(male_2011)
        self.female_2011 = int(female_2011)
        
        # Literacy rates and counts
        self.persons_literate_2001 = int(persons_literate_2001)
        self.literacy_rate_2001 = (self.persons_literate_2001 / self.persons) * 100 if self.persons > 0 else 0
        
        # Age counts 2001
        self.age_0_4_2001 = int(age_0_4_2001)
        self.age_5_14_2001 = int(age_5_14_2001)
        self.age_15_59_2001 = int(age_15_59_2001)
        self.age_60_plus_2001 = int(age_60_plus_2001)
        
        # Age percentages 2001
        self.age_0_4_pct_2001 = (self.age_0_4_2001 / self.persons) * 100 if self.persons > 0 else 0
        self.age_5_14_pct_2001 = (self.age_5_14_2001 / self.persons) * 100 if self.persons > 0 else 0
        self.age_15_59_pct_2001 = (self.age_15_59_2001 / self.persons) * 100 if self.persons > 0 else 0
        self.age_60_plus_pct_2001 = (self.age_60_plus_2001 / self.persons) * 100 if self.persons > 0 else 0
        
        # Age counts 2011
        self.age_0_29_2011 = int(age_0_29_2011)
        self.age_30_49_2011 = int(age_30_49_2011)
        self.age_50_2011 = int(age_50_2011)
        
        # Age percentages 2011
        self.age_0_29_pct_2011 = (self.age_0_29_2011 / self.population) * 100 if self.population > 0 else 0
        self.age_30_49_pct_2011 = (self.age_30_49_2011 / self.population) * 100 if self.population > 0 else 0
        self.age_50_pct_2011 = (self.age_50_2011 / self.population) * 100 if self.population > 0 else 0
        
        for y, val in pop_years_dict.items():
            setattr(self, f'population_{y}', int(val))

def index(request):
    # Fetch all records sorted to build dynamic dropdowns
    all_records = PopulationData.objects.order_by('state', 'district')
    
    # Structure mapping of {State: [District1, District2, ...]}
    state_districts_map = {}
    for record in all_records:
        if record.state and record.district:
            state = record.state.strip()
            district = record.district.strip()
            state_districts_map.setdefault(state, []).append(district)
            
    state_districts_json = json.dumps(state_districts_map)

    # Default context
    context = {
        'state_districts_json': state_districts_json,
        'states': sorted(list(state_districts_map.keys())),
        'selected_scope': 'district',
        'selected_state': None,
        'selected_district': None,
        'data': None,
        'forecast_years': [],
        'forecast_populations': []
    }

    if request.method == 'POST':
        selected_scope = request.POST.get('scope', 'district')
        selected_state = request.POST.get('state')
        selected_district = request.POST.get('district')
        
        try:
            if selected_scope == 'all':
                # Query all records in India
                qs = PopulationData.objects.all()
                title_label = "All India"
            elif selected_scope == 'state':
                # Filter records by selected State
                qs = PopulationData.objects.filter(state=selected_state)
                title_label = selected_state
            else:
                # Standard district filter
                qs = PopulationData.objects.filter(state=selected_state, district=selected_district)
                title_label = f"{selected_district} District, {selected_state}"

            if not qs.exists():
                raise PopulationData.DoesNotExist()

            # Execute database aggregation
            agg_fields = {
                'persons_sum': Sum('persons'),
                'population_sum': Sum('population'),
                'males_2001_sum': Sum('males'),
                'females_2001_sum': Sum('females'),
                'male_2011_sum': Sum('male'),
                'female_2011_sum': Sum('female'),
                'persons_literate_sum': Sum('persons_literate'),
                'age_0_4_2001_sum': Sum('x0_4_years'),
                'age_5_14_2001_sum': Sum('x5_14_years'),
                'age_15_59_2001_sum': Sum('x15_59_years'),
                'age_0_29_2011_sum': Sum('age_group_0_29'),
                'age_30_49_2011_sum': Sum('age_group_30_49'),
                'age_50_2011_sum': Sum('age_group_50'),
            }
            # Add population projection columns (2012-2026) dynamically
            for year in range(2012, 2027):
                agg_fields[f'pop_{year}_sum'] = Sum(f'population_{year}')

            totals = qs.aggregate(**agg_fields)

            # Retrieve sum results (fall back to 0 if database returns None)
            persons = totals['persons_sum'] or 0
            population = totals['population_sum'] or 0
            males_2001 = totals['males_2001_sum'] or 0
            females_2001 = totals['females_2001_sum'] or 0
            male_2011 = totals['male_2011_sum'] or 0
            female_2011 = totals['female_2011_sum'] or 0
            persons_literate = totals['persons_literate_sum'] or 0
            age_0_4_2001 = totals['age_0_4_2001_sum'] or 0
            age_5_14_2001 = totals['age_5_14_2001_sum'] or 0
            age_15_59_2001 = totals['age_15_59_2001_sum'] or 0
            age_0_29_2011 = totals['age_0_29_2011_sum'] or 0
            age_30_49_2011 = totals['age_30_49_2011_sum'] or 0
            age_50_2011 = totals['age_50_2011_sum'] or 0

            # Compute 2001 60+ group
            age_60_plus_2001 = persons - (age_0_4_2001 + age_5_14_2001 + age_15_59_2001)
            if age_60_plus_2001 < 0:
                age_60_plus_2001 = 0

            # Calculate aggregated Compound Annual Growth Rate (CAGR) as percentage
            if persons > 0 and population > 0:
                growth_rate = (((population / persons) ** 0.1) - 1) * 100
            else:
                growth_rate = 0.0

            pop_years_dict = {}
            for year in range(2012, 2027):
                pop_years_dict[year] = totals[f'pop_{year}_sum'] or 0

            # Wrap in DashboardData container
            data = DashboardData(
                persons, population, growth_rate,
                males_2001, females_2001, male_2011, female_2011,
                persons_literate,
                age_0_4_2001, age_5_14_2001, age_15_59_2001, age_60_plus_2001,
                age_0_29_2011, age_30_49_2011, age_50_2011,
                pop_years_dict
            )

            # Prepare data lists for drawing Chart.js line graph
            years = [2001, 2011]
            populations = [data.persons, data.population]
            for year in range(2012, 2027):
                years.append(year)
                populations.append(getattr(data, f'population_{year}'))

            context.update({
                'selected_scope': selected_scope,
                'selected_state': selected_state,
                'selected_district': selected_district,
                'title_label': title_label,
                'data': data,
                'forecast_years': years,
                'forecast_populations': populations,
                'gender_analysis': request.POST.get('gender_analysis') == 'on',
                'age_distribution': request.POST.get('age_distribution') == 'on',
                'literacy_education': request.POST.get('literacy_education') == 'on',
            })

        except PopulationData.DoesNotExist:
            context['error_message'] = "Selected geography not found in database."

    return render(request, 'dashboard/index.html', context)

