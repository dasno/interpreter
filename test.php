<?php
/*
Name: test.php
Description: Tester for interpret.py and parse.php. Part of IPP project.
Author: Daniel Pohancanik <xpohan03@stud.fit.vutbr.cz>
*/


$longopts  = array(
    "help",    
    "directory::",   
    "recursive",      
    "parse-script::",
    "int-script::",
    "parse-only",
    "int-only",
    "jexamxml::"
);

$directory = "";
$intScript = "";
$parseScript = "";
$jexamxml = "";


$shoropts = "";

$options = getopt($shoropts,$longopts);

#Aurgument processing segment.
if(isset($options['directory']))
{
    $directory = $options['directory'];
}

if(isset($options['int-script']))
{
    $intScript = $options['int-script'];
    
}

if(isset($options['parse-script']))
{
    $parseScript = $options['parse-script'];
    
}

if(isset($options['jexamxml']))
{
    $jexamxml = $options['jexamxml'];
    
}

if(isset($options['help']))
{
    if (count($options) > 1)
    {
        fwrite(STDERR, "Help cant be used with other arguments");
        exit(10);
    }
    else
    {
        echo "Skript (test.phpv jazyce PHP 7.4) bude sloužit pro automatické testování postupné aplikace parse.php a interpret.py.
        Skript projde zadaný adresář s testy a využije je pro automatické otestování správné funkčnosti obou předchozích programů včetně 
        vygenerování přehledného souhrnuv HTML 5 do standardního výstupu.\n";
        exit(0);
    }
}

if($directory == "")
{
    $directory = "./";
}

if($intScript == "")
{
    $intScript = "./interpret.py";
}

if($parseScript == "")
{
    $parseScript = "./parse.php";
}

if($jexamxml == "")
{
    $jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";
}

if (!file_exists($parseScript))
{
    exit(11);
}

if (!file_exists($intScript))
{
    exit(11);
}

if (!file_exists($jexamxml))
{
    exit(11);
}

if(isset($options['int-only']))
{
    if(isset($options['parse-only']))
    {
        exit(10);
    }
    if(isset($options['parse-script']))
    {
        exit(10);
    }
}

if(isset($options['parse-only']))
{
    if(isset($options['int-only']))
    {
        exit(10);
    }
    if(isset($options['int-script']))
    {
        exit(10);
    }
}

$optionsPath = explode('/', $jexamxml);
unset($optionsPath[count($optionsPath)-1]);
$optionsPath=implode("/", $optionsPath);

#Argument processing segment. END

$files = [];

#Getting file structure when recursive flag is set. Filepaths and filenames are appended into $files array.
if(isset($options['recursive']))
{
    $di = new RecursiveDirectoryIterator($directory);
    foreach (new RecursiveIteratorIterator($di) as $filename => $file) 
    {
        if($filename != "$directory." && $filename != "$directory..")
        {
            $files[] = "$filename\n";
        }
    }   
}
else
#Same as above but without recursion.
{
    $dir = new DirectoryIterator($directory);
foreach ($dir as $fileinfo) {
    if (!$fileinfo->isDot()) {
        $files[] = $fileinfo->getPath()."/".$fileinfo->getFilename()."\n";
    }
}
}




#Function for usort() method to use. It sorts files by their deepest directory. This is only used with recursion flag. File list isnt sorted in any way without
#recursion flag.
function customSortFunc($a, $b)
{
    $a = explode('/', $a);
    $b = explode('/', $b);

    if ($a[count($a)-2] > $b[count($b)-2])
    {
        return 1;
    }
    if ($a[count($a)-2] < $b[count($b)-2])
    {
        return -1;
    }

    if ($a[count($a)-2] == $b[count($b)-2])
    {
        return 0;
    }
}
$rc = "";
$results = [];

if(isset($options['recursive']))
{
    #Before mentioned sort.
    usort($files, "customSortFunc");
}


#Start of testing process. This loops iterates over each file in $files array.
foreach($files as $value)
{
    $output = "";
    $rc = "";
    $parsedOutput = "";
    $diffRc;
    $parseNotZero = "";
    #Makes sure we only iterate over files which have .src suffix. Rest are ignored.
    if (preg_match('/.*\.src/', $value))
    {

        
        #Getting rid of any suffix. Apropriate suffix is appended back manually when needed.
        $base = preg_replace('/\.[^.]+$/','',$value);

        #Checking whether .rc file for specific test exists. If not, apropriate file is created in filled with value of 0.
        if(!file_exists("$base.rc"))
        {
            $f = fopen("$base.rc", 'w+');
            fwrite($f, '0');
        }
        else
        {
            $f = fopen("$base.rc", 'r');
        }

        #Same as above but for .in files. Empty string is inserted in this case.
        if(!file_exists("$base.in"))
        {
            $refIn = fopen("$base.in", 'w+');
            fwrite($f, '');
        }
        
        #Getting error code from .rc file.
        $line = fgets($f);
        
        if(!isset($options['int-only']) && !isset($options['parse-only']))
        {
            #This version of parser test is only used when neither of int-only or parse-only flags are set.
            #Whole output is saved into $output and return code is saved into $parseRc 
            exec("php parse.php < $base.src", $output, $parseRc);
            if ($parseRc != 0)
            {
                #Setting up for further processing based on whether parser exited with non-zero return code and whether reference return code matched with parser rc.
                if($parseRc == $line)
                {
                    $parseNotZero = "pass";
                }
                else
                {
                    $parseNotZero = "fail";
                }
            }
            #Parsing of parser output
            foreach($output as $val)
            {
                $parsedOutput = $parsedOutput.$val;
            }
            #Setting $output to empty so another execs wont append their output to the end.
            $output = "";
        }

        if (isset($options['parse-only']))
        {
            exec("php parse.php < $base.src", $output, $rc);
            $output = implode($output);
        }
        
        
        
        #Temporary file to compare with.
        $tmpIntInput = fopen("tmp.in", 'w+');
        fwrite($tmpIntInput, $parsedOutput);

        if(isset($options['int-only']))
        {
            #This is bit of a work around. However these two execute interpret with correct source file and save output and rc in similar manner as parser exec.
            $output = shell_exec("python3.8 interpret.py --input=$base.in --source=$base.src");
            exec("python3.8 interpret.py --input=$base.in --source=$base.src", $throaway, $rc);
        }
        if(!isset($options['int-only']) && !isset($options['parse-only']))
        {
            if($parseNotZero != 'pass' and $parseNotZero != 'fail')
            {
                $output = shell_exec("python3.8 interpret.py --input=$base.in --source=tmp.in");
                exec("python3.8 interpret.py --input=$base.in --source=tmp.in", $throaway, $rc);
            
            }
        }
        
        

        $parsedOutput = $output;

        #Check whether .out file for this test exists.
        if(!file_exists("$base.out"))
        {
            $refOut = fopen("$base.out", 'w+');
            fwrite($f, '');
        }
        else
        {
            $refOut = fopen("$base.out", 'r');
        }
        
        

        $f1 = fopen("temp.out", 'w+');
        
        #Processing and creating of test result based on success of parser.
        if($parseNotZero == 'pass')
        {
            $testRes = ['PASS', $base, $parseRc, $line];
            $results[] = $testRes;

        }
        elseif( $parseNotZero == 'fail')
        {
            $testRes = ['FAIL', $base, $parseRc, $line];
            $results[] = $testRes;
        }
        else
        {
            if ($rc == $line)
            {
                if ($rc == 0)
                {
                    fwrite($f1, $parsedOutput);
                    #Comparing outputs. JexamXML is used for XML files and unix diff utlity is used otherwise. RC of compare is stored in $diffRc
                    if(isset($options['parse-only']))
                    {
                        exec("java -jar $jexamxml temp.out $base.out $optionsPath/options", $xd, $diffRc);
                    }
                    else
                    {
                        exec("diff $base.out temp.out", $xd, $diffRc);
                    }
                    
                    if($diffRc == 0)
                    {
                        $testRes = ['PASS', $base, $rc, $line];
                        $results[] = $testRes;
                    }
                    else
                    {
                        $testRes = ['FAIL', $base, $rc, $line];
                        $results[] = $testRes;
                    }

                }
                else
                {
                    $testRes = ['PASS', $base, $rc, $line];
                    $results[] = $testRes;
                }

            }
            else
            {
                $testRes = ['FAIL', $base, $rc, $line]; #vysledok, file, navratovy kod, ref. navratovy kod
                $results[] = $testRes;
            }
        }

        
        #exec("rm temp.out");
        fclose($f);
        fclose($f1);
    }
}


#Construction of HTML file.
$myFile = "filename.html";
$fh = fopen($myFile, 'w+'); 
fwrite($fh, "<!DOCTYPE html>\n<html>");
fwrite($fh, "<div align=\"center\">");
fwrite($fh, "<div style=\"background-color:#a3a3a3; width:50%;\">");
$toWrite = "";
$oldDirName = "";
if(isset($options["recursive"]))
{
    $tmp = explode('/', $results[0][1]);
    $oldDirName = $tmp[count($tmp)-2];
}

#fwrite($fh, "<p style=\"font-size:160%;\">$oldDirName</p>");

foreach($results as $value)
{

    $fname = explode('/', $value[1]);
    unset($fname[count($fname)-1]);
    $fname=implode("/", $fname);
    $dirname = $fname;
    if ($dirname != $oldDirName)
    {   $toWrite = $toWrite."</div>";
        $toWrite = $toWrite."<div style=\"background-color:#a3a3a3; width:50%;\">";
        $toWrite = $toWrite."<p style=\"font-size:160%;\">$dirname</p>";
    }
    if ($value[0] == 'PASS')
    {
        $toWrite = $toWrite."<div style=\"background-color:#82fc07;\">";
    }
    else
    {
        $toWrite = $toWrite."<div style=\"background-color:red;\">";
    }
    
    $toWrite = $toWrite."<p style=\"font-size:120%;\">Test name: $value[1]</p>";
    $toWrite = $toWrite."<p>Result: $value[0] <br> Expected Ret Code: $value[3] <br> Actual Ret Code: $value[2]<br></p>";
    $toWrite = $toWrite."</div>";
    $oldDirName = $dirname;
}
fwrite($fh, $toWrite);
fwrite($fh, "</div>");

$toPrint = file_get_contents("filename.html");
exec("rm filename.html");
echo $toPrint;
fclose($fh);