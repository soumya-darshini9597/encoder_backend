from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import csv
from .models import gear_value
from django.http import JsonResponse
import json
from django.utils.dateparse import parse_date
from datetime import datetime


@csrf_exempt
def gear_value_view(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            value_val = body.get('value', '')

            if not value_val:
                return JsonResponse({'error': 'Missing "gear_value" field.'}, status=400)

            # Save the value
            gear_value.objects.create(value=value_val)

            # Return all entries
            all_data = gear_value.objects.all().order_by('date', 'time')
            result = [
                {
                    'date': data.date.isoformat(),
                    'time': data.time.strftime('%H:%M:%S'),
                    'value': data.value
                }
                for data in all_data
            ]
            return JsonResponse(result, safe=False, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'GET':
        all_data = gear_value.objects.all().order_by('date', 'time')
        result = [
            {
                'date': data.date.isoformat(),
                'time': data.time.strftime('%H:%M:%S'),
                'value': data.value
            }
            for data in all_data
        ]
        return JsonResponse(result, safe=False)

    return JsonResponse({'error': 'Only GET and POST allowed'}, status=405)


@csrf_exempt
def filter_gear_value(request):
    if request.method == 'GET':
        from_date_str = request.GET.get('from_date')
        to_date_str = request.GET.get('to_date')

        if not from_date_str or not to_date_str:
            return JsonResponse({'error': 'Both "from_date" and "to_date" are required.'}, status=400)

        try:
            start = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            end = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use yyyy-MM-dd.'}, status=400)

        values = gear_value.objects.filter(date__gte=start, date__lte=end).order_by('date', 'time')

        if not values.exists():
            return JsonResponse({'error': 'No data found for the selected date range.'}, status=404)

        result = [
            {
                'date': item.date.isoformat(),
                'time': item.time.strftime('%H:%M:%S'),
                'gear_value': item.value 
            }
            for item in values
        ]

        return JsonResponse(result, safe=False)

    return JsonResponse({'error': 'Only GET allowed'}, status=405)


@csrf_exempt
def download_gear_value(request):
    if request.method == 'GET':
        # Get data in ascending order by date and time
        queryset = gear_value.objects.all().order_by('-date', '-time')[:10]

        # Prepare response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="gear_values.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Time', 'Value'])

        for item in queryset:
            writer.writerow([item.date.isoformat(), item.time.strftime('%H:%M:%S'), item.value])

        return response

    return JsonResponse({'error': 'Only GET allowed'}, status=405)