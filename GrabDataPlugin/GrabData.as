uint _curCP = 0;
int _lastCPTime = 0;

bool send_data_float(Net::Socket@ sock, float val)
{
	if (!sock.Write(val)) {
		print("INFO: Disconnected, could not send data.");
		return false;
	}
	return true;
}

void Main()
{
	while(true)
	{
		//Initialisation du socket pour envoyer les data
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


			//Récupé"ration du numéro du CP actuel et du temps au dernier CP
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
				
			// Sending data
			cc = send_data_float(sock, api.Speed);
			send_data_float(sock, api.Distance);
			if(race_state == SGamePlaygroundUIConfig::EUISequence::Finish) 
			{
				send_data_float(sock, 1.0f);
			}
			else send_data_float(sock, 0.0f);

			send_data_float(sock, _curCP); //Numero du dernier CP capturé
			send_data_float(sock, _lastCPTime); //Temps au dernier CP
			send_data_float(sock, api.CurrentRaceTime); //Temps actuel de la course
			send_data_float(sock, api.Position.x); //Position, nous avons besoin du x uniquement

			yield();  // this statement stops the script until the next frame
		}
		sock.Close();
		sock_serv.Close();
	}
}
