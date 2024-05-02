def ask_question(question):
    """Ask a question and get a response on a scale of 1-5."""
    response = None
    while response not in ['1', '2', '3', '4', '5']:
        print(question)
        response = input("Rate your understanding (1=Low, 5=High): ")
        if response not in ['1', '2', '3', '4', '5']:
            print("Invalid input. Please enter a number between 1 and 5.")
    return response

def main():
    questions = [
        "How well do you understand the process of Instant Runoff Voting?",
        "How clear is the method of eliminating candidates in IRV?",
        "How well do you understand the redistribution of votes in IRV?",
        "Can you explain the advantages of IRV over traditional voting systems?",
        "How confident are you in explaining IRV to someone else?"
    ]
    
    responses = []
    
    for question in questions:
        response = ask_question(question)
        responses.append(response)
    
    # Save the responses to a file
    with open('survey_responses.txt', 'w') as file:
        for question, response in zip(questions, responses):
            file.write(f"{question}: {response}\n")
    
    print("Thank you for completing the survey! Your responses have been saved.")

if __name__ == "__main__":
    main()
