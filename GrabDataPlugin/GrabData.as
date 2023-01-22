uint _curCP = 0;
int _lastCPTime = 0;

bool send_data_float(Net::Socket@ sock, float val)
{
	if (!sock.Write(val)) {
		// If this fails, the socket might not be open. Something is wrong!
		print("INFO: Disconnected, could not send data.");
		return false;
	}
	return true;
}

void Main()
{
	while(true)
	{
		auto sock_serv = Net::Socket();
		if (!sock_serv.Listen("127.0.0.1", 9000)) {
			print("Could not initiate server socket.");
			return;
		}
		print(Time::Now + " Waiting for incomming connection...");

		while(!sock_serv.CanRead()){
			yield();
		}
		print("Socket can read");
		auto sock = sock_serv.Accept();

		print(Time::Now + " Accepted incomming connection.");

		while (!sock.CanWrite()) {
			yield();
		}
		print("Socket can write");
		print(Time::Now + " Connected!");

		bool cc = true;
		while(cc)
		{
			CTrackMania@ app = cast<CTrackMania>(GetApp());
			CSmArenaClient@ playground = cast<CSmArenaClient>(app.CurrentPlayground);
			CSmArena@ arena = cast<CSmArena>(playground.Arena);
			auto player = arena.Players[0];
			CSmScriptPlayer@ api = cast<CSmScriptPlayer>(player.ScriptAPI);

			auto race_state = playground.GameTerminals[0].UISequence_Current;



			if(PlayerState::GetRaceData().PlayerState == PlayerState::EPlayerState::EPlayerState_Driving) {
			auto info = PlayerState::GetRaceData().dPlayerInfo;
			_curCP = info.NumberOfCheckpointsPassed;
			if(info.LatestCPTime > 0) {
				// LatestCPTime currently only exists for 1 frame
				_lastCPTime = info.LatestCPTime;
			}
			} else {
				_curCP = 0;
				_lastCPTime = 0;
			}
			//print(api.Position.x);

			// print("Current Race Time");
			// print(api.CurrentRaceTime);
			// print("Current CP");
			// print(_curCP);
			// print("Last CP Time");
			// print(_lastCPTime);

				
			// Sending data
			cc = send_data_float(sock, api.Speed);
			send_data_float(sock, api.Distance);
			if(race_state == SGamePlaygroundUIConfig::EUISequence::Finish) 
			{
				send_data_float(sock, 1.0f);
			}
			else send_data_float(sock, 0.0f);

			send_data_float(sock, _curCP);
			send_data_float(sock, _lastCPTime);
			send_data_float(sock, api.CurrentRaceTime);	
			send_data_float(sock, api.Position.x);		

			yield();  // this statement stops the script until the next frame
		}
		sock.Close();
		sock_serv.Close();
	}
}
