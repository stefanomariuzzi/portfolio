# imports
from datetime import datetime, timedelta
import time
from Bot import Bot

# function definition for report building
def report(bot):
    # number of dashes for prints
    dashes = 50
    # header print
    print('\n', '-'*dashes, 'INIZIO REPORT', '-'*dashes, sep='')
    # error vector definition
    errors = []
    # reset bot data
    bot.reset_data()
    # evaluate top_volume
    error, data = bot.top_volume()
    # append the error to the errors list
    errors.append(error)
    # if there is an error
    if error:
        # then print its message
        print('\n1. ERROR:', data)
    else:
        # else print the proper data
        text = '\n1. La criptovaluta con il volume maggiore delle '
        text += 'ultime 24 ore è {} ({}), con un volume di {:.2f}$'
        print(text.format(data['name'], data['symbol'], data['volume']))
    
    # evaluate headtail_per_change... etc (as before)
    error, data = bot.headtail_perc_change()
    errors.append(error)
    if error:
        print('\n2. ERROR:', data)
    else: 
        print('\n2.1 Le migliori 10 criptovalute (per incremento in percentuale delle ultime 24 ore) sono:')
        for cry in data['head']:
            print('\t+{:.2f}% - {} ({})'.format(cry[2], cry[0], cry[1]))
        print('\n2.2 Le peggiori 10 criptovalute (per incremento in percentuale delle ultime 24 ore) sono:')
        for cry in data['tail']:
            print('\t{:.2f}% - {} ({})'.format(cry[2], cry[0], cry[1]))   
        
    error, data = bot.topN_cap_price()
    errors.append(error)
    if error:
        print('\n3. ERROR:', data)
    else:
        text = '\n3. La quantità di denaro necessaria per acquistare una unità di ciascuna '
        text += 'delle prime 20 criptovalute è pari a {:.2f}$.\n   Le criptovalute utilizzate sono: '
        print(text.format(data['total']), end='')
        for i in range(2):
            print('\n\t', end='')
            for name in data['names'][i*10:(i+1)*10]:
                print(name, end=', ')
            
    error, data = bot.topV_vol_price()  
    errors.append(error)
    if error:
        print('\n4. ERROR:', data)
    else:     
        text = '\n\n4. La quantità di denaro necessaria per acquistare una unità di tutte le criptovalute'
        text += ' il cui volume delle ultime 24 ore sia superiore a 76.000.000$ è di {:.2f}$'
        print(text.format(data))       
    
    error, data = bot.check_profit()
    errors.append(error)
    if error:
        print('\n5. ERROR:', data)
    else:
        text = '\n5. La percentuale di guadagno o perdita che avreste realizzato se aveste '
        text += 'comprato una unità di ciascuna delle prime 20 criptovalute il giorno '
        text += 'prima (ipotizzando che la classifca non sia cambiata) è del {:.2f}%'
        print(text.format(data))
    
    error, file = bot.save_data()
    errors.append(error)
    if error:
        print('\n*. ERROR:', file)
    else:
        print('\n*. Dati salvati nel file', file)
        
    print('\n*. Per questo report sono stati utilizzati {} crediti.'.format(bot.credit_count))
    print('\n', '-'*dashes, '-FINE REPORT-', '-'*dashes, sep='')
    return sum(errors) > 0

# function definition for conversion between datetime.time() and seconds
def sec(t):
    return t.hour*60**2 + t.minute*60**1 + t.second*60**0 + t.microsecond*10**-6


if __name__ == '__main__':
    # KeyboardInterrupt exception handling
    try:
        # Bot initialization and printing
        bot = Bot()
        print('\nBot Inizializzato')
        # Private key loading
        error = 1
        while(error):
            input('Caricamento chiave privata, premere INVIO per continuare: ')
            error = bot.load_key('key.txt')
            if error:
                print('ERROR: Chiave non trovata, assicurarsi di avere il file \'key.txt\' con la chiave inserita\n')
            else:
                print('SUCCESS: Chiave caricata correttamente')
        # now date evaluation and printing for reference
        now = datetime.now()
        print('\nData: ', now, '\nNOTA: Per i prossimi inserimenti, utilizzare il formato ORA:MIN:SEC', sep='')
        # user input of the desired report hour and its period
        valid_in = False
        while(not valid_in):
            try:
                myt = input('\tA) Orario desiderato per la reportistica: ')
                myt = datetime.strptime(myt, '%H:%M:%S')
                valid_in = True
            except ValueError:
                print('\tERROR: Utilizzare il formato indicato')
        valid_in = False
        while(not valid_in):
            try:
                pet = input('\tB) Periodo di tempo tra due reports: ')                
                pet = datetime.strptime(pet, '%H:%M:%S')
                valid_in = True
            except ValueError:
                print('\tERROR: Utilizzare il formato indicato')
        
        # if chosen time is passed by 10 seconds today, set day to 1 else 0
        days = 1 if sec(now.time()) + 10 >= sec(myt.time()) else 0
        # chosen time conversion to datetime (if day is 1 the first report will be tommorw)
        myt = '{}-{}-{} {}:{}:{}'.format(now.year, now.month, now.day + days, myt.hour, myt.minute, myt.second)   
        myt = datetime.strptime(myt, '%Y-%m-%d %H:%M:%S') 
        # reports loop
        error = 0
        while(not error): 
            text = '\nIl prossimo scarico dati avverrà in data {}'
            text += '\nPremere CTRL + C per interrompere l\'esecuzione del programma'
            print(text.format(myt))
            # missing seconds evaluation
            seconds_missing = sec(myt.time()) - sec(datetime.now().time())
            # if tomorrow, add an entire day to it (in seconds)
            seconds_missing = seconds_missing if seconds_missing > 0 else seconds_missing + 24*60**2
            # sleep for the evaluated amount
            time.sleep(seconds_missing)
            # add chosen period to the chosen time of the day
            myt = myt + timedelta(hours=pet.hour, minutes=pet.minute, seconds=pet.second)
            # start report
            error = report(bot)
            # if an error occours
            if error:
                # then tell it to the user
                print('\nERROR: Esecuzione interrotta, visualizza il report per maggiori dettagli')
    # KeyboardInterrupt exception handling
    except KeyboardInterrupt:
        print('\n\nCTRL + C: Esecuzione interrotta')
        
