//============================================================================
// Name        : main.cpp
// Author      : FarabiAhmed
// Version     :
// Copyright   :
// Description : C++, Ansi-style
//============================================================================

#include <iostream>
#include <unordered_map>
#include <fstream>

#include "Environments/Environment.hpp"
#include "Environments/Gridworld.hpp"

#include "QIteration/CleaningRobotDeterministic.hpp"
#include "QIteration/GridWorld.hpp"

#include "ProbabilityDistributions/ProbabilityDistribution.hpp"
#include "ProbabilityDistributions/DiscreteDistribution.hpp"

#include "Miscellaneous/SmartVector.hpp"
#include "Miscellaneous/ConfigParser.hpp"

#include "Representations/Representation.hpp"
#include "Representations/StateActionValue.hpp"

#include "Agents/Agent.hpp"
#include "Agents/QIteration.hpp"
#include "Agents/TrajectoryBasedValueIteration.hpp"


using namespace std;


void help_menu(void)
{
	cout << "Gridworld with QIteration Unit Test Program							"<<endl;
}

int main()
{
	// For Random Number Generator
	srand(time(0));

	// Menu for user
	help_menu();

	// Get parameters from file
	ConfigParser cfg("config/config_gridworld.cfg");

	// Class Pointers
	Environment* environment 	= new Gridworld(cfg);
	Representation* value 		= new StateActionValue(*environment,cfg);
	Agent* agent 				= new QIteration(environment, value, cfg);

	SmartVector feature_centers(6);
	feature_centers = cfg.GetValueOfKey< SmartVector >("FEATURE_LOCATIONS");

	//Start Calculation
	agent->Start_Execution();

	//Show Q-Values
	value->Print_Value();

	//Show Policy
	environment->Display_Policy(*value);

	delete agent;
	delete environment;
	delete value;

	return 0;
}