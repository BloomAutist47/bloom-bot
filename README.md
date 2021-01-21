# Bloom Bot
A discord bot that takes bots from the AutoQuestWorld's portal site and sends them to the Discord Server.

# Bloom Bot Instructions



Please read the following carefully. If you complain to me and it turns out you didn't read the instructions, I'm going to fuck you up.

## Bot commands
`$b command command_value,...`  


## 【Search】
`$b b bot_name`             # Search for boats. Also accepts `boat`  as command.
`$b b all`                   	# Summons all bots. This is a long list. Is this a good idea?
`$b a author_name`	   # Finds a specific author. Also accepts `author`  as command. 
`$b a`                 	           # Shows a list of all authors.
`$b a u`             	           # Shows a list of bots with no recognized authors. Also accepts `unknown`  as command. 
`$b -set_name`    	        # Summons a set of bots, i.e. a category/list






## 【Set】For Privileged roles only
`$b set create set_name=[bot_name, bot_name, etc...]`         # Creates a set
`$b set append set_name=[bot_name, bot_name, etc...]`         # Adds bot to set
`$b set overwrite set_name=[bot_name, bot_name, etc...]`   # Overwrites a set
`$b set delete set_name`                                                                      # Deletes a set

**Note**:

- set_names should be single word

- bot_name can be found by using the search commands
- bot_name **MUST BE EXACTLY** the same name as the results.                                               





## 【Settings】For Privileged roles only

`$b u` 

> Updates database

`$b verify author @author`

> Adds author to the settings. This way, their name will be recognized by the algorithm. If they are not recognized, their bot will be added under the **Unknown** author. (Use this if a new author appears)





## 【 **Privileged Roles** 】

`roles:` Staff, Helper, Trial helper, Bot Maker