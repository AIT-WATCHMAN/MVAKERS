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

int main(int argc, char** argv)
{
  //Get filenames from command line
  std::string outname = "REEEE.root";
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
  cout << "DEFINE THE BRANCHES IN SIGNAL" << endl;
  //These are the histograms that are populated for the signal and background
//  TH1D* h_inner_dist_fv = new TH1D("h_inner_dist_fv", "h_inner_dist_fv",
//          100,0.0,20.0);
//  TH1D* h_inner_time = new TH1D("h_inner_time", "h_inner_time", 2000,0.0,100000.0);
//  h_inner_dist_fv->Sumw2();
//  h_inner_time->Sumw2();


  cout << "WE ABOUT TO LOAD FILES" << endl;
  //We fill the signal tree first open the file now
  //const string& filename = infile;
  for(int i=0;i<insigfiles.size();i++)
  {

    TFile* mafile = TFile::Open(insigfiles[i].c_str(),"READ");
    //Get the tree that has the entries
    TTree* T = (TTree*) mafile->Get("data");
    Double_t inner_dist_fv;
    Double_t inner_time;
  
    T->SetBranchAddress("inner_dist_fv",&inner_dist_fv);
    T->SetBranchAddress("inner_time",&inner_time);
  
    signal->Branch("inner_dist_fv",&inner_dist_fv);
    signal->Branch("inner_time",&inner_time);
 
    //loop through entries to get the inner_dist_fv and inner_time
    for (int entry=0; entry < T->GetEntries(); entry++)
    {
      T->GetEntry(entry);
  
      //First, we skip events defined as pathological
      if((inner_dist_fv == 0) || (inner_time == 0))
        continue;
      if((inner_dist_fv > 20.0) || (inner_time > 1000000.0))
        continue;
  
      signal->Fill();
    }
    delete T;
    mafile->Close();
    delete mafile;
  } 

  //And now the background branch
  for(int i=0;i<inbkgfiles.size();i++)
  {

    TFile* mafile = TFile::Open(inbkgfiles[i].c_str(),"READ");
    //Get the tree that has the entries
    TTree* T = (TTree*) mafile->Get("data");
    Double_t inner_dist_fv;
//    Double_t inner_time;
  
    T->SetBranchAddress("inner_dist_fv",&inner_dist_fv);
//    T->SetBranchAddress("inner_time",&inner_time);
  
    background->Branch("inner_dist_fv",&inner_dist_fv);
//    background->Branch("inner_time",&inner_time);
 
    //loop through entries to get the inner_dist_fv and inner_time
    for (int entry=0; entry < T->GetEntries(); entry++)
    {
      T->GetEntry(entry);
  
      //First, we skip events defined as pathological
      if((inner_dist_fv == 0)) // || (inner_time == 0))
        continue;
      if((inner_dist_fv > 20.0)) // || (inner_time > 1000000.0))
        continue;
  
      background->Fill();
    }
    delete T;
    mafile->Close();
    delete mafile;
  } 

//  h_inner_dist_fv->GetXaxis()->SetTitle("Inner Distance (m)");
//   h_inner_dist_fv->GetYaxis()->SetTitle("Events");

  cout << "WRITE THE FILE AND CLOSE" << endl;
  thehists->Write();
  thehists->Close();
} //End main
