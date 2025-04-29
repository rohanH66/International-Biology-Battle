import pandas as pd # type: ignore

def displayTeamRankings(average_list):
    index = 0
    for team in average_list:
        if index <= 34:
            if index <= 31:
                print(index + 1, team, average_list[team])
            elif index == 32:
                print("\nMISSED TOP 32 (either by tie break or score):")
            if index >= 32 and index <= 36:
                print(index + 1, team, average_list[team])
        index += 1

def displayIndividualRankings(average_list):
    index = 0
    for student in average_list:
        if index <= 9:
            print(index + 1, student, average_list[student])
        elif index <= 29:
            if index == 10:
                print("\nRANKINGS 11-30")
            print(index + 1, student, average_list[student])
        elif index <= 40:
            if index == 30:
                print("\nRANKINGS 31-40")
            print(index + 1, student, average_list[student])
        index += 1

def sort_dict(average_list, max_list):
    return dict(sorted(
        average_list.items(),
        key=lambda x: (x[1], max_list[x[0]]),  # <-- second key is the tiebreaker
        reverse=True
    ))
    
df = pd.read_csv('ibb_responses.csv')
teamNames = df['Select your team name (sorted alphabetically)']
indivdualNames = df["Full name (First and Last, as provided during registration)"]
scores, team_averages, team_count, score_dict = list(), dict(), dict(), dict()
team_max_individual = dict()  # <-- Add this dict to store max individual score per team

for temp in df["Score"]:
    scores.append(int(temp.split("/")[0]))

for i in range(len(scores)):  # calculate total score from the pretest (total, not average)
    currName, currTeam, currScore = indivdualNames[i].strip(), teamNames[i], scores[i]
    if currTeam not in team_averages:
        team_averages[currTeam], team_count[currTeam] = currScore, 1
        team_max_individual[currTeam] = currScore  # <-- First individual score is max so far
    else:
        team_count[currTeam] += 1
        team_averages[currTeam] += currScore
        team_max_individual[currTeam] = max(team_max_individual[currTeam], currScore)  # <-- update max
    score_dict[currName] = currScore

df1 = pd.read_csv('ibb_did_not_take_test.csv')
teamNamesDNT = df1["Team Name"]
scoresDNT = df1["Score"]

for i in range(len(teamNamesDNT)):  # add 0s for people who did not take the test
    currTeam, currScore = teamNamesDNT[i], int(scoresDNT[i])
    if currTeam not in team_averages:
        team_averages[currTeam], team_count[currTeam] = currScore, 1
        team_max_individual[currTeam] = currScore  # <-- track 0 or whatever they have
    else:
        team_count[currTeam] += 1
        team_averages[currTeam] += currScore
        team_max_individual[currTeam] = max(team_max_individual[currTeam], currScore)  # <-- update max

for team in team_averages:  # calculate average
    team_averages[team] /= team_count[team]

while True:
    choice = input("Would you like to remove a team? (Y/N): ")
    if choice.upper() != "Y":
        break
    teamName = input("Which team would you like to remove?: ")
    if teamName in team_averages:
        del team_averages[teamName]
    if teamName in team_max_individual:
        del team_max_individual[teamName]
    sorted_team_averages = sort_dict(team_averages, team_max_individual)
    displayTeamRankings(sorted_team_averages)

while True: 
    choice = input("Would you like to remove an individual? (Y/N): ")
    if choice.upper() != "Y":
        break
    studentName = input("Which individual would you like to remove?: ")
    if studentName in score_dict:
        del score_dict[studentName]
    sorted_score_dict = dict(sorted(score_dict.items(), key=lambda x: (x[1], [x[0]]), reverse=True))
    displayIndividualRankings(sorted_score_dict)    
    
print("\nFINAL TEAM RANKINGS: \n---------------------")

sorted_team_averages = sort_dict(team_averages, team_max_individual)
displayTeamRankings(sorted_team_averages)

print("\nFINAL INDIVIDUAL RANKINGS: \n---------------------")

sorted_score_dict = dict(sorted(score_dict.items(), key=lambda x: (x[1], [x[0]]), reverse=True))
displayIndividualRankings(sorted_score_dict)    