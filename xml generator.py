file = open('xml.txt', 'w')
words = open('word_list.txt', 'r')
words = words.readlines()

k = 0
for word in words:
	file.write('<string name="word{}">{}</string>\n'.format(k, word[:-1]))
	k += 1