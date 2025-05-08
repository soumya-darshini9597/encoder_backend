import time
import paho.mqtt.client as mqtt
from .models import gear_value  

# MQTT Configuration
MQTT_BROKER = 'mqttbroker.bc-pl.com'
MQTT_PORT = 1883  
MQTT_TOPIC = ['factory/gearbox1/input/rpm', 'factory/gearbox1/out1/rpm', 'factory/gearbox1/out2/rpm','factory/gearbox1/out3/rpm','factory/gearbox1/out4/rpm']  # List of topics
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'Bfl@2025'

# Callback when connected to broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker.")
        # Subscribe to each topic in the list
        for topic in MQTT_TOPIC:
            client.subscribe(topic, qos=0)  # Subscribe to each topic 
            print(f"Subscribed to topic: {topic}")
    else:
        print(f"Failed to connect. Code: {rc}")


from datetime import date
from gearapp.models import gear_value

def on_message(client, userdata, msg):
    try:
        # Delete all entries not from today
        today = date.today()
        gear_value.objects.exclude(date=today).delete() 

        payload = msg.payload.decode('utf-8')
        values = f"{msg.topic} | {payload}"
        print(f"Storing: {values}")

        # Save new value
        gear_value.objects.create(value=values) 

    except Exception as e:
        print(f"Error processing message: {e}")


        

# MQTT connection starter
def mqtt_connect():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Failed to connect to broker: {e}")
        return
    client.loop_start()

    try:
        while True:
            time.sleep(1)  # Keep the loop running
    except KeyboardInterrupt:
        print("Stopped by user.")
        client.loop_stop()
        client.disconnect()

# Run the MQTT connection
if __name__ == "__main__":
    mqtt_connect()
