import pandas as pd # type: ignore
import numpy as np # type: ignore
from reportlab.lib.pagesizes import letter # type: ignore
from reportlab.pdfgen import canvas # type: ignore

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
    all_entries = list(average_list.items())
    total_people = len(all_entries)

    previous_score = None
    rank_to_display = 0
    true_rank = 0
    count_displayed = 0
    top_40_names = set()

    print("RANKINGS 1–10")
    for i, (student, score) in enumerate(all_entries):
        true_rank += 1
        if score != previous_score:
            rank_to_display = true_rank

        if rank_to_display == 11 and count_displayed == 10:
            print("\nRANKINGS 11–30")
        elif rank_to_display == 31 and count_displayed == 30:
            print("\nRANKINGS 31–40")

        if rank_to_display > 40:
            break

        print(rank_to_display, student, score)
        top_40_names.add(student)
        previous_score = score
        count_displayed += 1

    # Get 75th percentile score (top 25% performers)
    scores_only = [score for _, score in all_entries]
    percentile_75_score = np.percentile(scores_only, 75)

    # Honorable mentions: not in top 40 and above 75th percentile cutoff
    honorable_mentions = [
        (student, score)
        for student, score in all_entries
        if student not in top_40_names and score >= percentile_75_score
    ]

    # Sort honorable mentions alphabetically
    honorable_mentions.sort(key=lambda x: x[0])

    print(f"\nHONORABLE MENTIONS, ALPHABETICAL ORDER (Top 25% by score not in top 40) — Score Cutoff: {percentile_75_score:.2f}")
    if not honorable_mentions:
        print("None")
        return

    previous_score = None
    rank_to_display = 0
    true_rank = 0

    for student, score in honorable_mentions:
        true_rank += 1
        if score != previous_score:
            rank_to_display = true_rank
        print(rank_to_display, student, score)
        previous_score = score



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

for i in range(len(teamNamesDNT)):
    currTeam, currScore = teamNamesDNT[i], int(scoresDNT[i])
    if currTeam not in team_averages:
        team_averages[currTeam], team_count[currTeam] = currScore, 1
        team_max_individual[currTeam] = currScore
    else:
        team_count[currTeam] += 1
        team_averages[currTeam] += currScore
        team_max_individual[currTeam] = max(team_max_individual[currTeam], currScore)  

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

# PDF CODE

def export_to_pdf(team_rankings, individual_rankings, filename="ibb_rankings.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    x_margin_left = 40
    x_margin_right = width / 2 + 20
    y = height - 50
    col = 0  # 0 = left, 1 = right

    def write_line(text, font="Helvetica", size=10, spacing=14):
        nonlocal y, col
        if y < 50:
            if col == 0:
                col = 1
                y = height - 50
            else:
                c.showPage()
                col = 0
                y = height - 50
        x = x_margin_left if col == 0 else x_margin_right
        c.setFont(font, size)
        c.drawString(x, y, text)
        y -= spacing

    # TEAM RANKINGS
    write_line("FINAL TEAM RANKINGS", font="Helvetica-Bold", size=14)
    write_line("---------------------")
    for i, (team, avg) in enumerate(team_rankings.items(), 1):
        write_line(f"{i}. {team} — {avg:.2f}")

    # NEW PAGE: INDIVIDUAL RANKINGS
    c.showPage()
    col = 0
    y = height - 50
    write_line("FINAL INDIVIDUAL RANKINGS", font="Helvetica-Bold", size=14, spacing=16)
    write_line("---------------------")

    # Section titles map and printed flags
    section_titles = {
        1: "RANKINGS 1–10",
        11: "RANKINGS 11–30",
        31: "RANKINGS 31–41"
    }
    printed_sections = set()

    all_entries = list(individual_rankings.items())
    top_40_names = set()
    previous_score = None
    rank_to_display = 0
    true_rank = 0

    for student, score in all_entries:
        true_rank += 1
        if score != previous_score:
            rank_to_display = true_rank

        # Print section title only once
        for start in section_titles:
            if start <= rank_to_display <= start + 9 and start not in printed_sections:
                write_line(section_titles[start], font="Helvetica-Bold", size=12, spacing=16)
                printed_sections.add(start)
                break

        if rank_to_display > 41:
            break

        write_line(f"{rank_to_display}. {student} — {score}")
        top_40_names.add(student)
        previous_score = score

    # HONORABLE MENTIONS
    scores_only = [score for _, score in all_entries]
    percentile_75_score = np.percentile(scores_only, 75)

    honorable_mentions = [
        (student, score)
        for student, score in all_entries
        if student not in top_40_names and score >= percentile_75_score
    ]
    honorable_mentions.sort(key=lambda x: x[0])  # Alphabetical

    # Force column break before honorable mentions
    if col == 0:
        col = 1
        y = height - 50
    else:
        c.showPage()
        col = 0
        y = height - 50

    write_line("HONORABLE MENTIONS, ALPHABETICAL ORDER (Top 25% by score not in top 40)", font="Helvetica-Bold", size=12)
    write_line(f"Cutoff Score: {percentile_75_score:.2f}", font="Helvetica", size=10, spacing=16)

    previous_score = None
    rank_to_display = 0
    true_rank = 0

    for student, score in honorable_mentions:
        true_rank += 1
        if score != previous_score:
            rank_to_display = true_rank
        write_line(f"{rank_to_display}. {student} — {score}")
        previous_score = score

    c.save()
    print(f"\nExported rankings to {filename}")

# Call the export function here:
export_to_pdf(sorted_team_averages, sorted_score_dict)