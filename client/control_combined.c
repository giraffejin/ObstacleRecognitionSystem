#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <wiringPi.h>
#include <softPwm.h>


#define PORT_s 3005
#define BUFF_SIZE 1024

#define IN1_PIN		1
#define IN2_PIN		4
#define IN3_PIN		5
#define IN4_PIN		6

#define SPEED 40

#define INIT_VALUE  				SPEED,  SPEED,  SPEED,   SPEED,          "INIT"
#define BACK_VALUE  		    	    SPEED,  0,         SPEED ,   0,          "BACK"
#define GO_VALUE  				0,         gSPEED,  0,           gSPEED,   "GO"
#define RIGHT_VALUE  				0,         SPEED,  SPEED,    0,          "RIGHT"
#define LEFT_VALUE  			    SPEED,  0,         0,           SPEED,   "LEFT"
#define STOP_VALUE  				0,         0,          0,          0,    "STOP"

void initDCMotor();
void controlMotor(int _IN1, int _IN2, int _IN3, int _IN4, char* msg);

int gSPEED = SPEED;

int main(void)
{
  int server_socket_s;
  int client_socket_s;
  int client_addr_size_s;
  int recv_s;


  struct sockaddr_in server_addr_s, client_addr_s;
  char buff_rcv_s[10];
  char pre_t[10]="";
  char pre_y[10] = "";
  char cur_t[10]="";
  char cur_y[10]="";

  if (wiringPiSetup() == -1)
      return 0;

  initDCMotor();

  /*open socket*/
  server_socket_s = socket(PF_INET,SOCK_STREAM,0);
  if(server_socket_s == -1)
  {
    printf("fail\n");
    exit(1);
  }

  memset(&server_addr_s,0,sizeof(server_addr_s));
  server_addr_s.sin_family = AF_INET;
  server_addr_s.sin_port = htons(PORT_s);
  server_addr_s.sin_addr.s_addr = htonl(INADDR_ANY);

  if(bind(server_socket_s, (struct sockaddr*)&server_addr_s, sizeof(server_addr_s))==-1)
 {
    printf("fail\n");
    exit(1);
  }

 /*wait connection*/
 printf("start listen...\n");
  if(listen(server_socket_s,10)==-1){
    printf("fail\n");
    exit(1);
  }

  printf("client wait\n");
  client_addr_size_s = sizeof(client_addr_s);
  client_socket_s = accept(server_socket_s, (struct sockaddr*)&client_addr_s, &client_addr_size_s);
  

  if(client_socket_s==-1){
    printf("fail\n");
    exit(1);
  }


  while (1) {
      /*Receive data*/
      printf("get data\n");
      recv_s = read(client_socket_s, buff_rcv_s, BUFF_SIZE);

      if (recv_s == 0) {
          break;
      }

      /*distinguish trafficlight result and yellow block detection result*/
      else {
          char* rcvt = strchr(buff_rcv_s, 't');
          char* rcvy = strchr(buff_rcv_s, 'y');
          if (rcvt != NULL) {
              strcpy(cur_t, buff_rcv_s);
          }
          else if (rcvy != NULL) {
              strcpy(cur_y, buff_rcv_s);
          }
      }

      /*speed up if signal changes to blink after green*/
      if (strcmp(cur_t, "tb") == 0)
      {
          if (strcmp(pre_t, "tg") == 0)
          {
              gSPEED = SPEED + 20;
              controlMotor(GO_VALUE);
              strcpy(cur_t, pre_t);
          }
          else
          {
              controlMotor(STOP_VALUE);
              printf("stop\n");
          }
      }
      else if (strcmp(cur_t, "tg") == 0)
      {
          controlMotor(GO_VALUE);
          printf("go\n");
      }
      else if (strcmp(cur_t, "tr") == 0)
      {
          controlMotor(STOP_VALUE);
          printf("stop\n");
      }
    else
    {
          if (strcmp(cur_y, "ya") == 0)
          {
              controlMotor(GO_VALUE);
              printf("go straight\n");
          }
          else if (strcmp(cur_y, "yl") == 0)
          {
              controlMotor(GO_VALUE);
              delay(3500);
              printf("turn left\n");
          }
          else if (strcmp(cur_y, "yr") == 0)
          {
              controlMotor(GO_VALUE);
              delay(1500);
              printf("turn right\n");
          }
          else if (strcmp(cur_y, "ys") == 0)
          {
              if (strcmp(pre_y, "yl") == 0) 
              {
                  controlMotor(LEFT_VALUE);
                  delay(1500);
                  controlMotor(STOP_VALUE);
              }
              else if (strcmp(pre_y, "yr") == 0)
              {
                  controlMotor(RIGHT_VALUE);
                  delay(1200);
                  controlMotor(STOP_VALUE);
              }
              else
              {
                  controlMotor(STOP_VALUE);
                  printf("stop\n");
              }
          }
    }

    /*save previous data(trafficlight)*/
    strcpy(pre_t, cur_t);
    strcpy(pre_y, cur_y);
  }

    printf("cur_t:%s\n", cur_t);
    printf("cur_y:%s\n", cur_y);

   controlMotor(STOP_VALUE);
   delay(1000);
   close(client_socket_s);
   return 0;
}

void initDCMotor()
{
    pinMode(IN1_PIN, SOFT_PWM_OUTPUT);
    pinMode(IN2_PIN, SOFT_PWM_OUTPUT);
    pinMode(IN3_PIN, SOFT_PWM_OUTPUT);
    pinMode(IN4_PIN, SOFT_PWM_OUTPUT);

    softPwmCreate(IN1_PIN, 0, SPEED);
    softPwmCreate(IN2_PIN, 0, SPEED);
    softPwmCreate(IN3_PIN, 0, SPEED);
    softPwmCreate(IN4_PIN, 0, SPEED);
}

void controlMotor(int _IN1, int _IN2, int _IN3, int _IN4, char* msg)
{
    softPwmWrite(IN1_PIN, _IN1);
    softPwmWrite(IN2_PIN, _IN2);
    softPwmWrite(IN3_PIN, _IN3);
    softPwmWrite(IN4_PIN, _IN4);
    printf("STATE - %s\n", msg);
}
