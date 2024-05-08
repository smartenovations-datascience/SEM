from gpio import *
import gpio 


# To turn pin high
# def main():
#     SET_PIN(Pin_num=gpio.DIO.BOARD_PIN_7)     #Board pin number 3 will be high
#     sleep(2)

def main():
    from gpio import DIO
    while 1:
        SET_PIN(Pin_num=DIO.BOARD_PIN_7)
        sleep(2)
        CLEAR_PIN(Pin_num=DIO.BOARD_PIN_7)     #Board pin number 3 will be low
        sleep(2)

# def main():
#     while 1:
#         status=GET_PIN_STATE(Pin_num=DIO.BOARD_PIN_37)  #Read the Board pin number 37
#         print(status)
#         sleep(2)




if __name__ == "__main__":
    GPIO_Init()
    main()