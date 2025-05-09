import time
import paho.mqtt.client as mqtt
from .models import gear_value  
from datetime import date
from gearapp.models import gear_value


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



topic_aliases = {
    "factory/gearbox1/input/rpm": "Input_rpm",
    "factory/gearbox1/out1/rpm": "Output1_rpm",
    "factory/gearbox1/out2/rpm": "Output2_rpm",
    "factory/gearbox1/out3/rpm": "Output3_rpm",
    "factory/gearbox1/out4/rpm": "Output4_rpm",
}

def on_message(client, userdata, msg):
    try:
        # Delete all entries not from today
        today = date.today()
        gear_value.objects.exclude(date=today).delete() 

        payload = msg.payload.decode('utf-8')

        # Get the alias for the topic or keep the original topic if no alias exists
        topic_alias = topic_aliases.get(msg.topic, msg.topic)

        # Create the new value format
        values = f"{topic_alias} : {payload}"
        print(f"Storing: {values}")

        # Save the new value
        gear_value.objects.create(value=values) 

        # Delete all entries not from today
        today = date.today()
        gear_value.objects.exclude(date=today).delete() 

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
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped by user.")
        client.loop_stop()
        client.disconnect()

# Run the MQTT connection
if __name__ == "__main__":
    mqtt_connect()
