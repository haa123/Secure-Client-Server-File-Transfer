import sysimport socketimport randomimport base64from Crypto.Cipher import AESimport osimport binasciiimport timeimport hashlibimport bbsdef byte_to_binary(n):    return ''.join(str((n & (1 << i)) and 1) for i in reversed(range(8)))def hex_to_binary(h):    return ''.join(byte_to_binary(ord(b)) for b in binascii.unhexlify(h))def analyse_message1(msg1, username_password_pairs):    global ns    #Display Message1 received from Client    #extracting parameters from Message1    client_id, request, p, g, gxaModp_client_cipher = [x.strip() for x in msg1.split('|')]    print "\n************ MESSAGE 1 received from Client ****************"    print "Message1 received from Client :", msg1     print "Client_ID                     :", client_id    print "p                             :", p    print "g                             :", g    print "g_Xamodp^pass                 :", gxaModp_client_cipher     print "***********************************************************\n"    global clientid     clientid = client_id    #DH parameters    p = int(p)    g = int(g)    #Server secret;random number    #generate random number of 160 bits and add DH parameter p to it    #xs = random.getrandbits(160) + p    xs = int(raw_input('input XB: ')) + p    #Random number,nonce Ns    seed = None        ns = str(bbs.blum_blum_shub(seed))    bin_ns = hex_to_binary(ns)    try:        #retrieve password for mentioned ClientID        password = username_password_pairs[client_id]    except KeyError:        #In case Client ID does not exist, display error message        print "Invalid Client ID"        return "Invalid Client ID"    #convert retrieved password to hexadecimal value    hexa_password = base64.b16encode(password)    #retrieve g^Xa mod p from Message1, Message1 XOR with password retrieved from Server    gxaModp_received_from_client = xor_encryption(gxaModp_client_cipher, hexa_password)    #If received g^Xa mod p contains alphabets, display error message    try:        int(gxaModp_received_from_client, 16)    except ValueError:        print "Invalid Password"        return 'Invalid Password'    #Message to be exchanged(g^Xs mod p): part of Ciphertext1    gxsModp = calculate_exponents(g, xs, p)    #Ciphertext1 (g^Xs mod p XOR password retrieved)    gxsModp_cipher1 = xor_encryption(gxsModp, hexa_password)    #Session key    global keyAS    #calculate (g^Xa mod p)^Xs mod p    keyAS = calculate_exponents(int(gxaModp_received_from_client), xs, p)    #pad key for AES, make it 16    keyAS = round_key(str(keyAS))    #Create object of AES encryption , specify ECB Mode    aes_obj_msg2 = AES.new(keyAS, AES.MODE_ECB)    #Ciphertext2((g^Xa mod p)^Xs mod p and Ns needed), Nonce(Ns) encrypted    ns_cipher2 = aes_obj_msg2.encrypt(ns)    #concatenate Ciphertext1 and Ciphertect2 to form Message2    msg2 = gxsModp_cipher1 + '|' + ns_cipher2    print "************ MESSAGE 2 Sent from Server ****************"    print "Xs                                    :", xs    print "g_Xsmodp                              :", gxsModp    print "g_Xsmodp^pass                         :", gxsModp_cipher1        print "Blum Blum Shub Generated Ns           :", ns    print "Blum Blum Shub Generated Ns  in binary:", bin_ns    print "Encrypted Ns                          :", ns_cipher2    print "MESSAGE2                              :", msg2    print "******************************************************\n\n"    #Message2    return msg2def analyse_message3(msg3):    name, encrypted_msg3 = [x.strip() for x in msg3.split('|')]    #Message3 from Client    encrypted_concatenated_ns_na = encrypted_msg3    #Create object of AES encryption , specify ECB Mode    cipher_obj = AES.new(keyAS, AES.MODE_ECB)    #Decrypted Ns||Na    decrypted_concatenated_ns_na = cipher_obj.decrypt(encrypted_concatenated_ns_na)    bin_decrypted_concatenated_ns_na = hex_to_binary(decrypted_concatenated_ns_na)    #extracting Ns, first 32 bits    received_ns = decrypted_concatenated_ns_na[:32]    bin_received_ns = hex_to_binary(received_ns)    #extracting Na,next 32 bits    received_na = decrypted_concatenated_ns_na[-32:]    bin_received_na = hex_to_binary(received_na)    print "************ MESSAGE 3 Received from Client **********"    print "Username                :", name    print "Encrypted(NA||NB)       :", encrypted_msg3    print "Decrypted(NA||NB)       :", decrypted_concatenated_ns_na    print "Decrypted(NA||NB) binary:", bin_decrypted_concatenated_ns_na    print "****************************************************\n\n"    #Compare received Ns and generated Ns    if received_ns == ns:        #If same, authenticate Client        print "Client Authenticated"    else:        #Authentication failed        print "Client Authentication Failed"        return "Client Authentication Failed"    #Encrypt Na with Kas    msg4_cipher = cipher_obj.encrypt(received_na)    print("msg4: " + msg4_cipher)    print "************ MESSAGE 4 Sent from Server ****************"    print "Decrypted Ns||Na             :", decrypted_concatenated_ns_na    print "NB                           :", bin_received_ns    print "NA                           :", bin_received_na    print "MESSAGE4                     :", msg4_cipher    print "******************************************************\n\n"    return msg4_cipher#pad key for AES, make it 16bytesdef round_key(key):    #find length of key    key_length = len(key)    #if length less than 16, padding needed    if key_length < 16:        #find difference        diff = 16 - key_length        #add zeroes        key += ('0' * diff)    else:        #return first 16 digits        return key[0:16]#xor operation for encryptiondef xor_encryption(gModp, hexa_password):    #get padded values of parameters passed    gModp, padded_hexa_password = pad(gModp, hexa_password)    #XOR operation performed    gModp_cipher = hex(int(str(gModp), 16) ^ int(str(padded_hexa_password), 16))    #convert to string    gModp_cipher = str(gModp_cipher)    #keep only desired value    gModp_cipher = gModp_cipher.replace('L', '').replace('0x', '')    return gModp_cipher# padding zeros for the xor operationdef pad(value1, value2):    #find the difference in lengths of two values passed    diff = len(str(value1)) - len(str(value2))    #if difference negative,make it a positive number    if diff < 0:        diff *= -1    #if length of value1 is greater, pad value2 to match lengths    if len(str(value1)) >= len(str(value2)):        value2 = value2 + ('0' * diff)    else:        #if length of value2 is greater, pad value1 to match lengths        value1 = value1 + ('0' * diff)    return value1, value2#calculate exponent value for parameters passeddef calculate_exponents(g, xa, p):    required_exponent = xa    #exponent greater than DH parameter p    if required_exponent >= p:        #Fermat theorem        fermat_value = required_exponent / (p - 1)        #value obtained after Fermats theorem        required_exponent = required_exponent - (fermat_value * (p - 1))    return pow(g, required_exponent, p)#compute Hash H(M) for the mentioned filedef hash_file(filename):    #Hashlib, SHA1 method used    m = hashlib.sha1()    #open the file for reading    with open(filename, 'rb') as fd:        while True:            #read data from file            chunk = fd.read(4096)            if len(chunk) == 0:                #if length received is zero, stop reading                break            else:                #add the read data to file                m.update(chunk)        #Message Digest MD        return m.hexdigest()#padding for AES Encryptiondef encryption_padding(value):    #pad zeroes to 16 bytes    value += (16 - len(value) % 16) * b'\0'    return valuedef main(argv):    #Maximum buffer size to hold sent/received data 1024bytes    global buffer_length    buffer_length = 1024    #10 ClientID/password combinations hard-coded    username_password_pairs = {'proj': 'projpass', 'security': 'securitypass', 'harika': "harikapass",                               'newsha': 'newshapass', 'admin': 'adminpass', 'admin1': 'adminpass',                               'file': 'filepass'}    #IP address of server and listening port number entered by user    try:        serverIP, port = argv        print "Listening at port ", port    except ValueError:        print "Specify IP Address and Port Number"        sys.exit()    # Create a socket to connect to server    # SOCK_STREAM:used for TCP connection    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #bind to mentioned port number    server_socket.bind(('', int(port)))    #listening on mentioned port number upto 5 connections    server_socket.listen(5)    #continue till connection terminates    while True:        #accept incoming client connection        connection, address = server_socket.accept()        #authentication attempts;maximum three allowed        auth_attempts = 3        while auth_attempts >= 1:            #To receive Message1 from Client            msg1 = connection.recv(buffer_length)            #parse the received Message1, form Message2            msg2 = analyse_message1(msg1, username_password_pairs)            #if Client sent Invalid Client ID,            if msg2 == "Invalid Client ID":                #decrement number of attempts                auth_attempts -= 1                #If three attempts exceeded, display error message                if auth_attempts == 0:                    msg2 = "Invalid Client ID. Max attempts exceeded"                    print "Max attempts exceeded"                #send error message to Client                connection.send(msg2)                #Allow credentials to be entered again                continue            #if Client sent Invalid Password,            if msg2 == "Invalid Password":                #decrement number of attempts                auth_attempts -= 1                #If three attempts exceeded, display error message                if auth_attempts == 0:                    msg2 = "Invalid Password. Max attempts exceeded"                    print "Max attempts exceeded"                #send error message to Client                connection.send(msg2)                #Allow credentials to be entered again                continue            #Send Message2 to Client            connection.send(msg2)            #Receive Message3 sent from client            msg3 = connection.recv(buffer_length)            #parse the received Message3, form Message4            msg4 = analyse_message3(msg3)            #In case, authentication fails,            if msg4 == "Client Authentication Failed":                #decrement attempts                auth_attempts -= 1                #Allow credentials to be entered again                continue            #Send Message4 to Client            connection.send(msg4)            time.sleep(1)            #compute Hash H(M)            file_hash = hash_file("cmpe209.txt")            #Create object of AES encryption , specify ECB Mode            aes_obj_for_file = AES.new(keyAS, AES.MODE_ECB)            #open the file for writing            with open("cmpe209.txt", 'rd') as fd:                while True:                    # Read line from the file                    line = fd.read()                    # Break at end of file                    if line == '':                        break                    #Send every line of the file to the server                    line = encryption_padding(line)                    #Send encypted file using Kas                    connection.send(aes_obj_for_file.encrypt(line))                fd.close()            time.sleep(3)            print "************ MESSAGE 5 Sent from Server ****************"            print "Hash            :", str(file_hash)            print "******************************************************\n\n"            print "*************************************************************"            print "Request File has been transferred to client"            print "Terminating connection with client"            print "**************************************************************\n\n"            #Send Hash H(M) to Client            connection.send(str(file_hash))            break        # Close client connection if client terminates        if auth_attempts > 0:            time.sleep(3)            connection.sendall("Connection Terminated")        break        connection.close()        if __name__ == '__main__':    main(sys.argv[1:])