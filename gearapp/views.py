from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import csv
from .models import gear_value
from django.http import JsonResponse
import json
from django.utils.timezone import now, make_aware
from datetime import datetime
from datetime import timedelta



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
        print(from_date_str,to_date_str)


        if not from_date_str or not to_date_str:
            return JsonResponse({'error': 'Both "from_date" and "to_date" are required.'}, status=400)

        try:
            start = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            print("111111111")
            end = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            print("2222222")
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use yyyy-MM-dd.'}, status=400)

        values = gear_value.objects.filter(date__gte=start, date__lte=end).order_by('date', 'time')

        if not values.exists():
            return JsonResponse({'error': 'No data found for the selected date range.'}, status=404)

        result = [
            {
                'date': item.date.isoformat(),
                'time': item.time.strftime('%H:%M:%S'),
                'value': item.value 
            }
            for item in values
        ]

        return JsonResponse(result, safe=False)

    return JsonResponse({'error': 'Only GET allowed'}, status=405)


@csrf_exempt
def download_gear_value(request):
    if request.method == 'GET':
        current_time = now()
        ten_minutes_ago = current_time - timedelta(minutes=10)

        queryset = gear_value.objects.all()

        filtered = []
        for item in queryset:
            item_datetime = datetime.combine(item.date, item.time)
            item_datetime = make_aware(item_datetime)  # Fix timezone issue here
            if ten_minutes_ago <= item_datetime <= current_time:
                filtered.append((item.date, item.time, item.value))

        filtered.sort(key=lambda x: datetime.combine(x[0], x[1]))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="gear_values.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Time', 'Value'])

        for date, time, value in filtered:
            writer.writerow([date.isoformat(), time.strftime('%H:%M:%S'), value])

        return response

    return JsonResponse({'error': 'Only GET allowed'}, status=405)
