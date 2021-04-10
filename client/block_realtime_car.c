#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <wiringPi.h>
#include <softPwm.h>

#define PORT_b 3003
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
void controlMotor(int _IN1, int _IN2, int _IN3, int _IN4, char *msg);

int gSPEED = SPEED;

int main(void)
{
  int server_socket;
  int client_socket;
  int client_addr_size;
  int recv;

  struct sockaddr_in server_addr, client_addr;
  char buff_rcv[10];
  char pre_rcv[10];
  
  if(wiringPiSetup() == -1)
		return 0;

  initDCMotor();

  /*open socket*/
  server_socket = socket(PF_INET,SOCK_STREAM,0);
  if(server_socket == -1)
  {
    printf("fail\n");
    exit(1);
  }
  
  /*setup server's IP and port*/
  memset(&server_addr,0,sizeof(server_addr));
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(PORT_b);
  server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
   
  /*bind the socket*/
  if(bind(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr))==-1)
 {
    printf("fail\n");
    exit(1);
  }

  printf("start listen...\n");
  /*wait for connection*/
  if(listen(server_socket,10)==-1){
    printf("fail\n");
    exit(1);
  }

  printf("client wait\n");
  client_addr_size = sizeof(client_addr);
  client_socket = accept(server_socket, (struct sockaddr*)&client_addr, &client_addr_size);
  

  if(client_socket==-1){
    printf("fail\n");
    exit(1);
  }
  while(1){
    /*Receive data*/
    printf("get data\n");
    recv = read(client_socket, buff_rcv, BUFF_SIZE);

    if(recv==0){
      break;
      }
    printf("receive:%s\n",buff_rcv);

    /*drive according to location of yellow block*/
    if(strcmp(buff_rcv,"ahead")==0)
    {
      controlMotor(GO_VALUE);
      printf("go straight\n");
    }
    else if(strcmp(buff_rcv,"left ")==0)
    {
      controlMotor(GO_VALUE);
      delay(3500);

      printf("turn left\n");
    }
    else if(strcmp(buff_rcv,"right")==0)
    {
      controlMotor(GO_VALUE);
      delay(1800);
      printf("turn right\n");
    }
    else if(strcmp(buff_rcv,"stop ")==0)
    {
        if (strcmp(pre_rcv, "left ") == 0) 
        {
            controlMotor(LEFT_VALUE);
            delay(1200);
            controlMotor(STOP_VALUE);
        }
        else if (strcmp(pre_rcv, "right") == 0)
        {
            controlMotor(RIGHT_VALUE);
            delay(750);
            controlMotor(STOP_VALUE);
        }
        else 
        {
            controlMotor(STOP_VALUE);
            printf("stop\n");
         }
    }
    strcpy(pre_rcv, buff_rcv);
  }
  controlMotor(STOP_VALUE);
  delay(1000);
  close(client_socket);
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

void controlMotor(int _IN1, int _IN2, int _IN3, int _IN4, char *msg)
{
		softPwmWrite(IN1_PIN, _IN1);
		softPwmWrite(IN2_PIN, _IN2);
		softPwmWrite(IN3_PIN, _IN3);
		softPwmWrite(IN4_PIN, _IN4);			
		printf("STATE - %s\n", msg) ;			
}

