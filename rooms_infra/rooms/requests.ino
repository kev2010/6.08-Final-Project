void ping_online(char* user) {
  char body[200]; //for body;
  sprintf(body, "username=%s", user); //generate body, posting to User, 1 step
  int body_len = strlen(body); //calculate body length (for header reporting)
  sprintf(request_buffer, "POST http://608dev-2.net/sandbox/sc/team079/rooms_infra/Python_Files/login.py HTTP/1.1\r\n");
  strcat(request_buffer, "Host: 608dev-2.net\r\n");
  strcat(request_buffer, "Content-Type: application/x-www-form-urlencoded\r\n");
  sprintf(request_buffer + strlen(request_buffer), "Content-Length: %d\r\n", body_len); //append string formatted to end of request buffer
  strcat(request_buffer, "\r\n"); //new line from header to body
  strcat(request_buffer, body); //body
  strcat(request_buffer, "\r\n"); //header
  Serial.println(request_buffer);
  do_http_request("608dev-2.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);
  Serial.println(response_buffer);
}

void host_room_post_req(char* user, uint8_t selection){
  char body[200]; //for body;
  sprintf(body, "username=%s&game_id=%d", user, selection); //generate body, posting to User, 1 step
  int body_len = strlen(body); //calculate body length (for header reporting)
  sprintf(request_buffer, "POST http://608dev-2.net/sandbox/sc/team079/rooms_infra/Python_Files/host_lobby.py HTTP/1.1\r\n");
  strcat(request_buffer, "Host: 608dev-2.net\r\n");
  strcat(request_buffer, "Content-Type: application/x-www-form-urlencoded\r\n");
  sprintf(request_buffer + strlen(request_buffer), "Content-Length: %d\r\n", body_len); //append string formatted to end of request buffer
  strcat(request_buffer, "\r\n"); //new line from header to body
  strcat(request_buffer, body); //body
  strcat(request_buffer, "\r\n"); //header
  Serial.println(request_buffer);
  do_http_request("608dev-2.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);
  Serial.println(response_buffer);
}


void join_room_post_req(char* user, uint8_t selection){ // change me
  char body[200]; //for body;
  sprintf(body, "username=%s&game_id=%d", user, selection); //generate body, posting to User, 1 step
  int body_len = strlen(body); //calculate body length (for header reporting)
  sprintf(request_buffer, "POST http://608dev-2.net/sandbox/sc/team079/rooms_infra/Python_Files/join_lobby.py HTTP/1.1\r\n");
  strcat(request_buffer, "Host: 608dev-2.net\r\n");
  strcat(request_buffer, "Content-Type: application/x-www-form-urlencoded\r\n");
  sprintf(request_buffer + strlen(request_buffer), "Content-Length: %d\r\n", body_len); //append string formatted to end of request buffer
  strcat(request_buffer, "\r\n"); //new line from header to body
  strcat(request_buffer, body); //body
  strcat(request_buffer, "\r\n"); //header
  Serial.println(request_buffer);
  do_http_request("608dev-2.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);
  Serial.println(response_buffer);
}
