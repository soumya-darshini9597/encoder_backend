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
            client.subscribe(topic, qos=0)  # Subscribe to each topic with QoS 0 (you can change QoS if needed)
            print(f"Subscribed to topic: {topic}")
    else:
        print(f"Failed to connect. Code: {rc}")


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        values = f"{msg.topic} | {payload}"
        print(f"Storing: {values}")

        gear_value.objects.create(value=values)  # Save values

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
