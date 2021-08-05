from pyngrok import ngrok
# https://pyngrok.readthedocs.io/en/latest/
# !pip install pyngrok


# Open a HTTP tunnel on the default port 80
# <NgrokTunnel: "http://<public_sub>.ngrok.io" -> "http://localhost:80">
http_tunnel = ngrok.connect(5000, "http")

# https://pyngrok.readthedocs.io/en/latest/api.html#pyngrok.ngrok.NgrokTunnel
tunnels = ngrok.get_tunnels()
test=tunnels[0].public_url
test=test.split("//")
webhook_url="https://{}/callback".format(test[1])
print(webhook_url)
#print("copy to line developer's webhook text slot: \n")
#print("https://developers.line.me/console/")

ngrok_process = ngrok.get_ngrok_process()

try:
    # Block until CTRL-C or some other terminating event
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print(" Shutting down server.")

    ngrok.kill()
    