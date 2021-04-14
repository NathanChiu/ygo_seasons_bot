def convert_ydk(filename):
    #filename=input("Enter your Collection/Deck's filename: ")
    with open('%s.ydk'%filename,'r') as temp_file:
        #remove deck category lines
        newlist = [line.replace('#main','').replace('#extra','').replace('!side','').replace('\n','') for line in temp_file]
        print('List Formatting Complete.')

        #del newlist[0] # delete header of deck file
        #del newlist[0] # delete useless newline
        print('File Headers Stripped.')
        newlist = list(filter(None,newlist))
        print('Empty Lines Cleaned.')

        my_dict = {i:newlist.count(i) for i in newlist} #
        newlist = list(my_dict.items())
        print('Duplicate Entries Grouped.')

    with open('%s.lflist.conf'%filename,'w') as f:
        f.write('!AFKyle Seasons\n')
        f.write('$whitelist\n')
        for i in newlist:
            if i[1] >3:
                f.write('%s 3 --\n'%(i[0]))
            else:
                f.write('%s %i --\n'%(i[0],i[1]))
    print('File Generated: %s.lflist.conf' %(filename))

#ydkconverter.convert_ydk(filename=input("Enter your Collection/Deck's filename: "))
