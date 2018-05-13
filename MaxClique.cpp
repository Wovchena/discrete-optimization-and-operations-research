#include <fstream>
#include <string>
#include <sstream>
#include <iostream>
#include <vector>
#include <list>
#include <chrono>
#include <cstdlib>
#include <time.h>
#include <algorithm>
#include <thread>
#include <mutex>
#include <chrono>
#include <thread>

using namespace std;

struct Color
{
	Color(int v, int c): v(v), color(c) {}
	int v;
	int color;
};
struct Degree
{
	Degree(int v, int degree) : v(v), degree(degree) {}
	int v;
	int degree;
	bool operator<(const Degree & d) const { return degree > d.degree; }
};
int n;
vector<vector<bool>> m; // connection matrix
vector<Degree> sortedV;
list<int> maxQ; // should be mutexed
unsigned char numberOfFreeThread; // should be mutexed
mutex QM; // cliQue Mutex
mutex PM; // numberOfFreeThread Mutex
int maxColor = 1;

void addToQ(list<int> * curQ, int nInSorted)
{
	curQ->push_back(sortedV[nInSorted].v);
	QM.lock();
	if (curQ->size() > maxQ.size())
		maxQ = *curQ;
	if (maxQ.size() == maxColor)
	{
		QM.unlock();
		curQ->pop_back();
		return;
	}
	int strangeIndex = maxQ.size() - curQ->size(); // required degree of candidate
	QM.unlock();

	vector<int> candidatesNInSorted; // id of v in sortedV that can be added to q
	candidatesNInSorted.reserve(n);
	for (int i = nInSorted + 1; i <= n; i++)
	{
		if (sortedV[nInSorted].degree > strangeIndex)
			candidatesNInSorted.push_back(i);
	}
	if (candidatesNInSorted.size() <= strangeIndex) // low number of candidates
	{
		curQ->pop_back();
		return;
	}

	for (const int i : candidatesNInSorted)
	{
		bool f = 0;
		for (const int cliqueV : *curQ)
		{
			if (1 != m[sortedV[i].v][cliqueV])
			{
				f = 1;
				break;
			}
		}
		if (0 == f)
		{
			addToQ(curQ, i);
		}
	}
	curQ->pop_back();
}

void threadF(int nInSorted)
{
	PM.lock();
	numberOfFreeThread--;
	PM.unlock();
	list<int> * curQ = new list<int>();
	addToQ(curQ, nInSorted);
	delete(curQ);
	PM.lock();
	numberOfFreeThread++;
	PM.unlock();
}

int main(int argc, char ** argv)
{
	// get file name and build graph
	ifstream inFile;
	inFile.open(argv[1]);
	string s;
	vector<pair<int, int> > e;
	while (getline(inFile, s))
	{
		if ('e' == s[0])
		{
			istringstream l(s.erase(0, 2));
			int a, b;
			l >> a >> b;
			e.push_back(pair<int, int>(a, b));
			if (n < a) n = a;
			if (n < b) n = b;
		}
	}
	m.resize(n + 1); // connection matrix
	for (int i = 0; i <= n; i++)
	{
		m[i].assign(n + 1, 0);
	}
	for (const auto &i : e)
	{
		m[i.second][i.first] = m[i.first][i.second] = 1;
	}

	//create and sort V
	for (int i = 0; i <= n; i++)
	{
		int degree = 0;
		for (const auto j : m[i])
			degree += j;
		sortedV.push_back(Degree(i, degree));
	}
	std::sort(sortedV.begin(), sortedV.end());

	//color graph
	vector<Color> colored;
	colored.assign(n+1, Color(-1, -1));
	for (int j = 0; j <= n; j++) // v in sortedV
	{
		int f2 = 0;
		for (int i = 1; i <= maxColor; i++) // color
		{
			int f = 0;
			for (int k = 0; k < j; k++) // prev V
			{
				if (m[sortedV[j].v][sortedV[k].v] == 1 && colored[k].color == i)
				{
					f = 1; // bad color
					break;
				}
			}
			if (0 == f)
			{
				colored[j] = Color(sortedV[j].v, i);
				f2 = 1;
				break;
			}
		}
		if (0 == f2)
		{
			maxColor++;
			colored[j] = Color(sortedV[j].v, maxColor);
		}
	}

	// get time limit
	time_t limit = strtol(argv[2], nullptr, 10);
	time_t started = time(0);

	// get threads number
	int allowedThreadsN;
	if (4 == argc)
		allowedThreadsN = strtol(argv[3], nullptr, 10);
	else 
		allowedThreadsN = 1;
	numberOfFreeThread = allowedThreadsN; // no working threads for now

	// job
	try {
		int unprocessedN = 0; // id of the first unprocessed v in sortedV
		while (unprocessedN <= n)
		{
			if (numberOfFreeThread > 0)
			{
				thread t(threadF, unprocessedN);
				unprocessedN++;
				t.detach();
			}
			auto elapsed = time(0) - started;
			if (elapsed > limit)
				throw 42;
		}
		while (numberOfFreeThread != allowedThreadsN) // wait for last threads
		{
			std::this_thread::sleep_for(std::chrono::milliseconds(1000)); // do not spam checks
			auto elapsed = time(0) - started;
			if (elapsed > limit)
				throw 42;
		}
	}
	catch (int)
	{
		cout << "0 ";
		QM.lock();
		for (const int i : maxQ)
			cout << i << ' ';
		cout << endl;
		QM.unlock();
		return 0;
	}

	cout << maxQ.size() << ' ';
	for (const int i : maxQ)
		cout << i << ' ';
	cout << endl;
	return 0;
}
//for /r %i in (*) do "Max Clique.exe" %i 385
