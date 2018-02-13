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
    Double_t good_pos, good_pos_prev;
    Double_t good_dir, good_dir_prev;
    Double_t u, u_prev;
    Double_t v, v_prev;
    Double_t w, w_prev;
    Double_t x, x_prev;
    Double_t y, y_prev;
    Double_t r, r_prev;
    Double_t z, z_prev;

    T->SetBranchAddress("interevent_dist_fv",&interevent_dist_fv);
    T->SetBranchAddress("interevent_time",&interevent_time);
    T->SetBranchAddress("pe",&pe);
    T->SetBranchAddress("pe_prev",&pe_prev);
    T->SetBranchAddress("n9",&n9);
    T->SetBranchAddress("n9_prev",&n9_prev);
    T->SetBranchAddress("nhit",&nhit);
    T->SetBranchAddress("nhit_prev",&nhit_prev);
    T->SetBranchAddress("u",&u);
    T->SetBranchAddress("u_prev",&u_prev);
    T->SetBranchAddress("v",&v);
    T->SetBranchAddress("v_prev",&v_prev);
    T->SetBranchAddress("w",&w);
    T->SetBranchAddress("w_prev",&w_prev);
    T->SetBranchAddress("r",&r);
    T->SetBranchAddress("r_prev",&r_prev);
    T->SetBranchAddress("x",&x);
    T->SetBranchAddress("x_prev",&x_prev);
    T->SetBranchAddress("y",&y);
    T->SetBranchAddress("y_prev",&y_prev);
    T->SetBranchAddress("z",&z);
    T->SetBranchAddress("z_prev",&z_prev);
    T->SetBranchAddress("good_pos",&good_pos);
    T->SetBranchAddress("good_pos_prev",&good_pos_prev);
    T->SetBranchAddress("good_dir",&good_dir);
    T->SetBranchAddress("good_dir_prev",&good_dir_prev);

    signal->Branch("interevent_dist_fv",&interevent_dist_fv);
    signal->Branch("interevent_time",&interevent_time);
    signal->Branch("pe",&pe);
    signal->Branch("pe_prev",&pe_prev);
    signal->Branch("n9",&n9);
    signal->Branch("n9_prev",&n9_prev);
    signal->Branch("nhit",&nhit);
    signal->Branch("nhit_prev",&nhit_prev);
    signal->Branch("u",&u);
    signal->Branch("u_prev",&u_prev);
    signal->Branch("v",&v);
    signal->Branch("v_prev",&v_prev);
    signal->Branch("w",&w);
    signal->Branch("w_prev",&w_prev);
    signal->Branch("r",&r);
    signal->Branch("r_prev",&r_prev);
    signal->Branch("x",&x);
    signal->Branch("x_prev",&x_prev);
    signal->Branch("y",&y);
    signal->Branch("y_prev",&y_prev);
    signal->Branch("z",&z);
    signal->Branch("z_prev",&z_prev);
    signal->Branch("good_pos",&good_pos);
    signal->Branch("good_pos_prev",&good_pos_prev);
    signal->Branch("good_dir",&good_dir);
    signal->Branch("good_dir_prev",&good_dir_prev);

    //loop through entries to get the inner_dist_fv and n9
    for (int entry=0; entry < T->GetEntries(); entry++)
    {
      T->GetEntry(entry);
  
      //We will only run with events with a valid fit and sensical values
      //These should be taken into account when calculating S & B efficiencies
      if((interevent_dist_fv <= 0) || (interevent_dist_fv > 50000.0) || (interevent_time <= 0))
        continue;
      if(good_dir < 0 || good_pos <= 0 || n9 <= -1 || r > 100.0 || r <= 0 || abs(z) > 100.0 || abs(z) <= 0 )
        continue;
      if(good_dir_prev < 0 || good_pos_prev <= 0 || n9_prev <= -1 || r_prev > 100.0 || r_prev <= 0 || abs(z_prev) > 100.0 || abs(z_prev) <= 0 )
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
    Double_t good_pos,good_pos_prev;
    Double_t good_dir, good_dir_prev;
    Double_t u, u_prev;
    Double_t v, v_prev;
    Double_t w, w_prev;
    Double_t x, x_prev;
    Double_t y, y_prev;
    Double_t r, r_prev;
    Double_t z, z_prev;

   
    T->SetBranchAddress("interevent_dist_fv",&interevent_dist_fv);
    T->SetBranchAddress("interevent_time",&interevent_time);
    T->SetBranchAddress("pe",&pe);
    T->SetBranchAddress("pe_prev",&pe_prev);
    T->SetBranchAddress("n9",&n9);
    T->SetBranchAddress("n9_prev",&n9_prev);
    T->SetBranchAddress("nhit",&nhit);
    T->SetBranchAddress("nhit_prev",&nhit_prev);
    T->SetBranchAddress("u",&u);
    T->SetBranchAddress("u_prev",&u_prev);
    T->SetBranchAddress("v",&v);
    T->SetBranchAddress("v_prev",&v_prev);
    T->SetBranchAddress("w",&w);
    T->SetBranchAddress("w_prev",&w_prev);
    T->SetBranchAddress("r",&r);
    T->SetBranchAddress("r_prev",&r_prev);
    T->SetBranchAddress("x",&x);
    T->SetBranchAddress("x_prev",&x_prev);
    T->SetBranchAddress("y",&y);
    T->SetBranchAddress("y_prev",&y_prev);
    T->SetBranchAddress("z",&z);
    T->SetBranchAddress("z_prev",&z_prev);
    T->SetBranchAddress("good_pos",&good_pos);
    T->SetBranchAddress("good_pos_prev",&good_pos_prev);
    T->SetBranchAddress("good_dir",&good_dir);
    T->SetBranchAddress("good_dir_prev",&good_dir_prev);

    background->Branch("interevent_dist_fv",&interevent_dist_fv);
    background->Branch("interevent_time",&interevent_time);
    background->Branch("pe",&pe);
    background->Branch("pe_prev",&pe_prev);
    background->Branch("n9",&n9);
    background->Branch("n9_prev",&n9_prev);
    background->Branch("nhit",&nhit);
    background->Branch("nhit_prev",&nhit_prev);
    background->Branch("u",&u);
    background->Branch("u_prev",&u_prev);
    background->Branch("v",&v);
    background->Branch("v_prev",&v_prev);
    background->Branch("w",&w);
    background->Branch("w_prev",&w_prev);
    background->Branch("r",&r);
    background->Branch("r_prev",&r_prev);
    background->Branch("x",&x);
    background->Branch("x_prev",&x_prev);
    background->Branch("y",&y);
    background->Branch("y_prev",&y_prev);
    background->Branch("z",&z);
    background->Branch("z_prev",&z_prev);
    background->Branch("good_pos",&good_pos);
    background->Branch("good_pos_prev",&good_pos_prev);
    background->Branch("good_dir",&good_dir);
    background->Branch("good_dir_prev",&good_dir_prev);

    //loop through entries to get the inner_dist_fv and n9
    for (int entry=0; entry < T->GetEntries(); entry++)
    {
      T->GetEntry(entry);
  
      //We will only run with events with a valid fit and sensical values
      //These should be taken into account when calculating S & B efficiencies
      if((interevent_dist_fv <= 0) || (interevent_dist_fv > 50000.0) || (interevent_time <= 0))
        continue;
      if(good_dir < 0 || good_pos <= 0 || n9 <= -1 || r > 100.0 || r <= 0 || abs(z) > 100.0 || abs(z) <= 0 )
        continue;
      if(good_dir_prev < 0 || good_pos_prev <= 0 || n9_prev <= -1 || r_prev > 100.0 || r_prev <= 0 || abs(z_prev) > 100.0 || abs(z_prev) <= 0 )
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
