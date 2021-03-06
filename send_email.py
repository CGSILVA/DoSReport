import re
import smtplib
import sys

#Old Imports
#from email.MIMEMultipart import MIMEMultipart
#from email.MIMEText import MIMEText
#from email.Utils import formatdate

#New Imports
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

import settings


class Send_Email():


    def email_validator(self, email):

        if re.match('^[_A-Za-z0-9-]+(\\.[_A-Za-z0-9-]+)*@[A-Za-z0-9]+(\\.[A-Za-z0-9]+)*(\\.[A-Za-z]{2,})$', email) is not None:
            return 1
        return 0

    def send_email(self, email, ips, atk=0):

        if not self.email_validator(email):
            print (email, '- Email inválido')
        elif len(settings.EMAIL_PASSWORD) == 2 and len(settings.SYSADM) > 0:
            if not self.email_validator(settings.EMAIL_PASSWORD[0]):
                print (email, '- Email inválido')
            else:
                msg = MIMEMultipart()
                msg['From'] = settings.EMAIL_PASSWORD[0]
                msg['To'] = email
                msg['Date'] = formatdate(localtime=True)

                #Mensagem do email
                if atk == 0:
                    msg['Subject'] = 'Alerta de DoS'
                    message = []
                    message.append(
                        'Identificamos que seu endereço web está sofrendo um ataque DoS do IP {}.'.format(ips))
                    if settings.BLOQUEAR_ATAQUES:
                        message.append(
                            '\n\nO IP foi bloquado seguindo a regra de iptables \"{}\".'.format(settings.IPTABLES))
                    message.append(
                        '\n\n\tEsta mensagem foi gerada automaticamente pelo sistema, não responda este e-mail.')
                    message = ''.join(message)
                    msg.attach(MIMEText(message))
                elif atk == 1:
                    msg['Subject'] = 'Alerta de DDoS'
                    message = []
                    message.append(
                        'Identificamos que seu endereço web está sofrendo um ataque DDoS dos IPs:\n')
                    for ip in ips:
                        message.append('\n>> {}'.format(ip))
                    if settings.BLOQUEAR_ATAQUES:
                        message.append(
                            '\n\nOs IPs foram bloquados seguindo a regra de iptables \"{}\".'.format(settings.IPTABLES))
                    message.append(
                        '\n\n\tEsta mensagem foi gerada automaticamente pelo sistema, não responda este e-mail.')
                    message = ''.join(message)
                    msg.attach(MIMEText(message))

                try:
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(settings.EMAIL_PASSWORD[0], settings.EMAIL_PASSWORD[1])
                    server.sendmail(settings.EMAIL_PASSWORD[0], email, msg.as_string())
                    if atk == 0:
                        ipEnviar = ips
                    else:
                        ipEnviar = []
                        for ip in ips:
                            ipEnviar.append(ip)
                        ipEnviar = ', '.join(ipEnviar)

                    print ('Email enviado para {} sobre o ataque dos IPs: {}'.format(email, ipEnviar))
                except smtplib.SMTPServerDisconnected:
                    sys.stderr.write('ERRO: Falha ao enviar email. Servidor desconectado.')
                except smtplib.SMTPRecipientsRefused:
                    sys.stderr.write('ERRO: Falha ao enviar email. Destinatários recusados.')
                except smtplib.SMTPResponseException:
                    sys.stderr.write('ERRO: Falha ao enviar email. Falha durante o recebimento de resposta.')
                except smtplib.SMTPAuthenticationError:
                    sys.stderr.write('ERRO: Falha ao enviar email. Falha com a autentificação do email.')
                except smtplib.SMTPConnectError:
                    sys.stderr.write('ERRO: Falha ao enviar email. Falha ao se conectar com o servidor.')
                except smtplib.SMTPDataError:
                    sys.stderr.write('ERRO: Falha ao enviar email. Servidor recusou a mensagem enviada.')
                except smtplib.SMTPHeloError:
                    sys.stderr.write('ERRO: Falha ao enviar email. Servidor recusou mensagem de HELO')
                except smtplib.SMTPSenderRefused:
                    sys.stderr.write('ERRO: Falha ao enviar email. Falha com endereço de origem')
                except smtplib.SMTPException:
                    sys.stderr.write('ERRO: Falha ao enviar email.')
                finally:
                    server.close()
        elif len(settings.EMAIL_PASSWORD) == 0:
            sys.stderr.write('ERRO: Email para enviar os alertas ainda não foi configurado. Verifique o arquivo settings.py')
        else:
            sys.stderr.write('ERRO: Falha nas variáveis de email informadas. Verifique o arquivo settings.py.')
