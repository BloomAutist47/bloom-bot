# Bloom Bot
A discord bot that takes bots from the AutoQuestWorld's [portal site](http://adventurequest.life/) and sends them to the Discord Server.

Join [AutoQuestWorlds](https://discord.gg/NQBemdbnyW).

## Bloom Bot Instructions

Please read the following carefully. If you complain to me and it turns out you didn't read the instructions, I'm going to fuck you up.



## 【Bot commands】
1. `$b command command_value,...`  




## 【Search】
1. `$b b bot_name`  - Search for boats. Also accepts `boat`  as command.
2. `$b b all`  - Summons all bots. This is a long list. Is this a good idea?
3. `$b a author_name` - Finds a specific author. Also accepts `author`  as command. 
4. `$b a` - Shows a list of all authors.
5. `$b a u`  - Shows a list of bots with no recognized authors. Also accepts `unknown`  as command. 
6. `$b -set_name` - Summons a set of bots, i.e. a category/list



## 【Set】For Privileged roles only

Sets are a list or group of manually added bots.

1. `$b set create set_name=[bot_name, bot_name, etc...]` - Creates a set.
2. `$b set append set_name=[bot_name, bot_name, etc...]` - Adds bot to set.
3. `$b set overwrite set_name=[bot_name, bot_name, etc...]`  - Overwrites a set.
4. `$b set delete set_name` - Deletes a set.

**Note**:

- set_names should be single word

- bot_name can be found by using the search commands
- bot_name **MUST BE EXACTLY** the same name as the results.                                               



## 【Settings】For Privileged roles only

1. `$b u`  - Updates database
2. `$b verify author @author` - Adds author to the settings. This way, their name will be recognized by the algorithm. If they are not recognized, their bot will be added under the **Unknown** author. (Use this if a new author appears)



## 【 **Privileged Roles** 】

`roles:` Staff, Helper, Trial helper, Bot Maker