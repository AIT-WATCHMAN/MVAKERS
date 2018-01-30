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
  std::string outname = "IBD_ACC_SB.root";
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
    Double_t interevent_dist_fv;
    Double_t interevent_time;
    Double_t pe, pe_prev; 
    Double_t n9, n9_prev;
    Double_t nhit, nhit_prev;
    Double_t pos_goodness, pos_goodness_prev;
    Double_t dir_goodness, dir_goodness_prev;
    Double_t reco_r, reco_r_prev;
    Double_t reco_z, reco_z_prev;

    T->SetBranchAddress("interevent_dist_fv",&interevent_dist_fv);
    T->SetBranchAddress("interevent_time",&interevent_time);
    T->SetBranchAddress("pe",&pe);
    T->SetBranchAddress("pe_prev",&pe_prev);
    T->SetBranchAddress("n9",&n9);
    T->SetBranchAddress("n9_prev",&n9_prev);
    T->SetBranchAddress("nhit",&nhit);
    T->SetBranchAddress("nhit_prev",&nhit_prev);
    T->SetBranchAddress("reco_r",&reco_r);
    T->SetBranchAddress("reco_r_prev",&reco_r_prev);
    T->SetBranchAddress("reco_z",&reco_z);
    T->SetBranchAddress("reco_z_prev",&reco_z_prev);
    T->SetBranchAddress("pos_goodness",&pos_goodness);
    T->SetBranchAddress("pos_goodness_prev",&pos_goodness_prev);
    T->SetBranchAddress("dir_goodness",&dir_goodness);
    T->SetBranchAddress("dir_goodness_prev",&dir_goodness_prev);

    signal->Branch("interevent_dist_fv",&interevent_dist_fv);
    signal->Branch("interevent_time",&interevent_time);
    signal->Branch("pe",&pe);
    signal->Branch("pe_prev",&pe_prev);
    signal->Branch("n9",&n9);
    signal->Branch("n9_prev",&n9_prev);
    signal->Branch("nhit",&nhit);
    signal->Branch("nhit_prev",&nhit_prev);
    signal->Branch("reco_r",&reco_r);
    signal->Branch("reco_r_prev",&reco_r_prev);
    signal->Branch("reco_z",&reco_z);
    signal->Branch("reco_z_prev",&reco_z_prev);
    signal->Branch("pos_goodness",&pos_goodness);
    signal->Branch("pos_goodness_prev",&pos_goodness_prev);
    signal->Branch("dir_goodness",&dir_goodness);
    signal->Branch("dir_goodness_prev",&dir_goodness_prev);

    //loop through entries to get the inner_dist_fv and n9
    for (int entry=0; entry < T->GetEntries(); entry++)
    {
      T->GetEntry(entry);
  
      //We will only run with events with a valid fit and sensical values
      //These should be taken into account when calculating S & B efficiencies
      if((interevent_dist_fv <= 0) || (interevent_dist_fv > 15000.0) || (interevent_time <= 0))
        continue;
      if(dir_goodness < 0.1 || pos_goodness <= 0 || n9 <= -1 || reco_r > 5.42 || reco_r <= 0 || abs(reco_z) > 5.42 || abs(reco_z) <= 0 )
        continue;
      if(dir_goodness_prev < 0.1 || pos_goodness_prev <= 0 || n9_prev <= -1 || reco_r_prev > 5.42 || reco_r_prev <= 0 || abs(reco_z_prev) > 5.42 || abs(reco_z_prev) <= 0 )
        continue;
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
    
    Double_t n9,n9_prev;
    Double_t pe,pe_prev;
    Double_t nhit, nhit_prev;
    Double_t pos_goodness,pos_goodness_prev;
    Double_t dir_goodness, dir_goodness_prev;
    Double_t reco_r, reco_r_prev;
    Double_t reco_z, reco_z_prev;
    
    T->SetBranchAddress("interevent_dist_fv",&interevent_dist_fv);
    T->SetBranchAddress("interevent_time",&interevent_time);
    T->SetBranchAddress("pe",&pe);
    T->SetBranchAddress("pe_prev",&pe_prev);
    T->SetBranchAddress("n9",&n9);
    T->SetBranchAddress("n9_prev",&n9_prev);
    T->SetBranchAddress("nhit",&nhit);
    T->SetBranchAddress("nhit_prev",&nhit_prev);
    T->SetBranchAddress("reco_r",&reco_r);
    T->SetBranchAddress("reco_r_prev",&reco_r_prev);
    T->SetBranchAddress("reco_z",&reco_z);
    T->SetBranchAddress("reco_z_prev",&reco_z_prev);
    T->SetBranchAddress("pos_goodness",&pos_goodness);
    T->SetBranchAddress("pos_goodness_prev",&pos_goodness_prev);
    T->SetBranchAddress("dir_goodness",&dir_goodness);
    T->SetBranchAddress("dir_goodness_prev",&dir_goodness_prev);

    background->Branch("interevent_dist_fv",&interevent_dist_fv);
    background->Branch("interevent_time",&interevent_time);
    background->Branch("pe",&pe);
    background->Branch("pe_prev",&pe_prev);
    background->Branch("n9",&n9);
    background->Branch("n9_prev",&n9_prev);
    background->Branch("nhit",&nhit);
    background->Branch("nhit_prev",&nhit_prev);
    background->Branch("reco_r",&reco_r);
    background->Branch("reco_r_prev",&reco_r_prev);
    background->Branch("reco_z",&reco_z);
    background->Branch("reco_z_prev",&reco_z_prev);
    background->Branch("pos_goodness",&pos_goodness);
    background->Branch("pos_goodness_prev",&pos_goodness_prev);
    background->Branch("dir_goodness",&dir_goodness);
    background->Branch("dir_goodness_prev",&dir_goodness_prev);

    //loop through entries to get the inner_dist_fv and n9
    for (int entry=0; entry < T->GetEntries(); entry++)
    {
      T->GetEntry(entry);
  
      //We will only run with events with a valid fit and sensical values
      //These should be taken into account when calculating S & B efficiencies
      if((interevent_dist_fv <= 0) || (interevent_dist_fv > 15000.0) || (interevent_time <= 0))
        continue;
      if(dir_goodness < 0.1 || pos_goodness <= 0 || n9 <= -1 || reco_r > 5.42 || reco_r <= 0 || abs(reco_z) > 5.42 || abs(reco_z) <= 0 )
        continue;
      if(dir_goodness_prev < 0.1 || pos_goodness_prev <= 0 || n9_prev <= -1 || reco_r_prev > 5.42 || reco_r_prev <= 0 || abs(reco_z_prev) > 5.42 || abs(reco_z_prev) <= 0 )
        continue;
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
