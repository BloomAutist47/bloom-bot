import pypresence

RPC = pypresence.Presence(client_id="799639690176495637", pipe=0) 
y = RPC.connect()
x = RPC.update(state="Rich Presence using pypresence!", details="A test of qwertyquerty's Python Discord RPC wrapper, pypresence!")
print(x)
print(y)

# from discoIPC import ipc
# client = ipc.DiscordIPC('799639690176495637')
# client.connect()
# activity = {
#     'state': 'In the white house.'}

# client.update_activity(activity)

while True:
	continue

