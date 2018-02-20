////////////////////////////////////////////////////////////////////
/// \file SBMaker.cc
///
/// \Code that takes in root ntuples associated with a background, and
//  \ntuples associated with a signal.  The program outpus a single
//  \ROOT file with histograms that give the PDFs of all variables
//  \specified and used in the histogram.  Format is set up for use
//  \with TMVA.
////////////////////////////////////////////////////////////////////
#include <TH1D.h>
#include <TH1F.h>
#include <TCut.h>
#include <TH2.h>
#include <TFile.h>
#include <TTree.h>
#include <TCanvas.h>
#include <TStyle.h>
#include <TLegend.h>
#include <TApplication.h>

#include <iostream>
#include <typeinfo>
#include <string>
#include <map>
#include <iterator>
using namespace std;

//vector<string> MVAvars()
//{
  //const char *vinit[] = {"inner_dist_fv","n9"};
  //int length = sizeof(vinit_/sizeof(vinit[0]);
  //std::vector<string> vec(vinit, vinit+length);
  //return vec;
//}

int main(int argc, char** argv)
{
  //Get filenames from command line
  //std::vector<string> variables = MVAvars();
  std::string outname = "NEUTRON_ACCSINGLES_SB.root";
  std::vector<string> insigfiles;
  std::vector<string> inbkgfiles;
  bool gettingsigfiles = false;
  bool gettingbkgfiles = false;
  bool haveoutput = false;
  for(int i=1; i<argc; i++)
  {
    if( argv[i] == string("-s") )
    {
      gettingbkgfiles = false;
      gettingsigfiles = true;
      cerr << "found it" << endl;
      continue;
    }
    if( argv[i] == string("-b") )
    {
      gettingsigfiles = false;
      gettingbkgfiles = true;
      continue;
    }
   if( gettingbkgfiles == true )
    {
      inbkgfiles.push_back(argv[i]);
      continue;
    }
    if( gettingsigfiles == true )
    {
      insigfiles.push_back(argv[i]);
      continue;
    }
 }

 //I don't even use these; it crashed on my cluster without them
  // Define our histograms
  //Define histograms to fill in
  //TApplication* myapp = new TApplication("myapp",0,0);

  //TCanvas* c1 = new TCanvas("c1","c1",800,1200);
  for(int i=0; i<inbkgfiles.size();i++)
    cout << inbkgfiles[i] << endl;

  TFile* thehists = new TFile(outname.c_str(), "CREATE");

  //Define our trees 
  TTree *signal = new TTree("signal","signal_tree");
  TTree *background = new TTree("background", "background_tree");
  //These are the histograms that are populated for the signal and background
//  TH1D* h_inner_dist_fv = new TH1D("h_inner_dist_fv", "h_inner_dist_fv",
//          100,0.0,20.0);
//  TH1D* h_n9 = new TH1D("h_n9", "h_n9", 2000,0.0,100000.0);
//  h_inner_dist_fv->Sumw2();
//  h_n9->Sumw2();


  //We fill the signal tree first open the file now
  //const string& filename = infile;
  for(int i=0;i<insigfiles.size();i++)
  {

    TFile* mafile = TFile::Open(insigfiles[i].c_str(),"READ");
    //Get the tree that has the entries
    TTree* T = (TTree*) mafile->Get("data");
    Double_t pe; 
    Double_t n9;
    Double_t nhit;
    Double_t good_pos;
    Double_t good_dir;
    Double_t u;
    Double_t v;
    Double_t w;
    Double_t x;
    Double_t y;
    Double_t r;
    Double_t z;

    T->SetBranchAddress("pe",&pe);
    T->SetBranchAddress("n9",&n9);
    T->SetBranchAddress("nhit",&nhit);
    T->SetBranchAddress("u",&u);
    T->SetBranchAddress("v",&v);
    T->SetBranchAddress("w",&w);
    T->SetBranchAddress("r",&r);
    T->SetBranchAddress("x",&x);
    T->SetBranchAddress("y",&y);
    T->SetBranchAddress("z",&z);
    T->SetBranchAddress("good_pos",&good_pos);
    T->SetBranchAddress("good_dir",&good_dir);

    signal->Branch("pe",&pe);
    signal->Branch("n9",&n9);
    signal->Branch("nhit",&nhit);
    signal->Branch("u",&u);
    signal->Branch("v",&v);
    signal->Branch("w",&w);
    signal->Branch("r",&r);
    signal->Branch("x",&x);
    signal->Branch("y",&y);
    signal->Branch("z",&z);
    signal->Branch("good_pos",&good_pos);
    signal->Branch("good_dir",&good_dir);

    //loop through entries to get the inner_dist_fv and n9
    for (int entry=0; entry < T->GetEntries(); entry++)
    {
      T->GetEntry(entry);
      signal->Fill();
    }
    delete T;
    mafile->Close();
    delete mafile;
  } 
  cout << "FINISHED SIGNAL FILES" << endl;
  //And now the background branch
  for(int i=0;i<inbkgfiles.size();i++)
  {

    TFile* mafile = TFile::Open(inbkgfiles[i].c_str(),"READ");
    //Get the tree that has the entries
    TTree* T = (TTree*) mafile->Get("CombAcc");
    Double_t interevent_dist_fv;
    Double_t interevent_time;
    
    Double_t n9;
    Double_t pe;
    Double_t nhit;
    Double_t good_pos;
    Double_t good_dir;
    Double_t u;
    Double_t v;
    Double_t w;
    Double_t x;
    Double_t y;
    Double_t r;
    Double_t z;

   
    T->SetBranchAddress("pe",&pe);
    T->SetBranchAddress("n9",&n9);
    T->SetBranchAddress("nhit",&nhit);
    T->SetBranchAddress("u",&u);
    T->SetBranchAddress("v",&v);
    T->SetBranchAddress("w",&w);
    T->SetBranchAddress("r",&r);
    T->SetBranchAddress("x",&x);
    T->SetBranchAddress("y",&y);
    T->SetBranchAddress("z",&z);
    T->SetBranchAddress("good_pos",&good_pos);
    T->SetBranchAddress("good_dir",&good_dir);

    background->Branch("pe",&pe);
    background->Branch("n9",&n9);
    background->Branch("nhit",&nhit);
    background->Branch("u",&u);
    background->Branch("v",&v);
    background->Branch("w",&w);
    background->Branch("r",&r);
    background->Branch("x",&x);
    background->Branch("y",&y);
    background->Branch("z",&z);
    background->Branch("good_pos",&good_pos);
    background->Branch("good_dir",&good_dir);

    //loop through entries to get the inner_dist_fv and n9
    for (int entry=0; entry < T->GetEntries(); entry++)
    {
      T->GetEntry(entry);
      background->Fill();
    }
    delete T;
    mafile->Close();
    delete mafile;
  } 


  cout << "WRITE THE FILE AND CLOSE" << endl;
  thehists->Write();
  thehists->Close();
} //End main
