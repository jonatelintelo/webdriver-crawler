import os
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from tabulate import tabulate
from collections import Counter


crawl_data = "./crawl_data"
output_folder = './analysis'

#1. Add a table on the number of failures encountered during each crawl
def nr_of_failures_encountered():
    # Initialize defaultdict to keep track of error types
    error_counts = defaultdict(lambda: defaultdict(int))

    # Iterate through crawl data and count errors
    for file in os.listdir(crawl_data):
        if file.endswith("_accept.json"):
            filepath = os.path.join(crawl_data, file)
            with open(filepath, 'r') as f:
                data = json.load(f)
                errors = data['errors']
                error_counts['page_load_timeout']['crawl-accept'] += errors['page_load_timeout']
                error_counts['dns']['crawl-accept'] += errors['dns']
                error_counts['consent_click']['crawl-accept'] += errors['consent_click'] 
        elif file.endswith("_noop.json"):
            filepath = os.path.join(crawl_data, file)
            with open(filepath, 'r') as f:
                data = json.load(f)
                errors = data['errors']
                error_counts['page_load_timeout']['crawl-noop'] += errors['page_load_timeout']
                error_counts['dns']['crawl-noop'] += errors['dns']
                error_counts['consent_click']['crawl-noop'] = "NA"

    # Format the values names as requested
    new_column_values = {
        'page_load_timeout': 'Page load timeout',
        'dns': 'DNS Error',
        'consent_click': 'Consent click error'
    }

    # Format the table headers
    headers = ['Error type', 'Crawl-accept', 'Crawl-noop']
    
    # Format the table rows
    rows = []
    for error_type in error_counts.keys():
        crawl_accept_value = error_counts[error_type]['crawl-accept'] 
        crawl_noop_value = error_counts[error_type]['crawl-noop'] 
        row = [
            new_column_values.get(error_type, error_type),
            crawl_accept_value,
            crawl_noop_value
        ]
        rows.append(row)

    # Format the table
    table = tabulate(rows, headers=headers, tablefmt='pipe')

    # Create the table visualization
    fig, ax = plt.subplots(figsize=(6, 3))

    # Hide axes
    ax.axis('off')
    
    # Set the font properties for the table
    table = ax.table(cellText=rows,
                    colLabels=headers,
                    loc='center',
                    cellLoc='center')

    # Apply the formatting to the table cells
    for i in range(0, len(rows)):
        table[0, i].get_text().set_fontweight('bold')

    for i in range(0,len(rows)+1):
        table[i,0].get_text().set_horizontalalignment("left")

    for i in range(1,len(rows)+1):
        for j in range(1,len(headers)):
            table[i,j].get_text().set_horizontalalignment("right")

    # Adjust the table layout
    table.scale(1, 1.5)
    table.set_fontsize(7)

    # Save the table as a PNG image
    output_file = 'failure_table.png'
    output_path = os.path.join(output_folder, output_file)
    print(f"Table saved as {'./analysis/failure_table.png'}")
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close(fig)

nr_of_failures_encountered()

#2. Compare data from the two crawls using a series of box plots
def box_plots_metrics():
    # Create a defaultdict to store the box plot data
    crawl_data_box_plots = defaultdict(lambda: defaultdict(list))

    # Iterate over the crawl data files
    for file in os.listdir(crawl_data):
        if file.endswith("_accept.json") or file.endswith("_noop.json"):
            filepath = os.path.join(crawl_data, file)
            with open(filepath, 'r') as f:
                data = json.load(f)
                crawl_type = "crawl-accept" if file.endswith("_accept.json") else "crawl-noop"
                crawl_data_box_plots['page_load_time'][crawl_type].append((data['pageload_end_ts'] - data['pageload_start_ts']))
                crawl_data_box_plots['number_of_requests'][crawl_type].append(len(data['request_headers']))
                crawl_data_box_plots['number_of_distinct_third_parties'][crawl_type].append(len(data['third_party_request_domains']))
                crawl_data_box_plots['number_of_distinct_tracker_domains'][crawl_type].append(len(data['tracker_domains']))
                crawl_data_box_plots['number_of_distinct_tracker_entities'][crawl_type].append(len(data['tracker_entities']))

    for metric, crawl_types in crawl_data_box_plots.items():
        plt.figure()
        box_colors = ['lightblue', 'orange']
        # Create the box plot with custom box colors
        bp = plt.boxplot([crawl_types['crawl-accept'], crawl_types['crawl-noop']],
                        patch_artist=True,  # Enable box filling
                        capprops=dict(color='black'),
                        whiskerprops=dict(color='black'),
                        flierprops=dict(marker='o', markerfacecolor='black', markersize=5),
                        medianprops=dict(color='red')
                        )
        
        # Set the colors for the boxes
        for patch, color in zip(bp['boxes'], box_colors):
            patch.set_facecolor(color)

        # Set the x-axis tick labels
        plt.xticks([1, 2], ['Crawl-accept', 'Crawl-noop'])
        
        # Set labels and title
        plt.xlabel('Crawl Type')
        plt.ylabel(metric.replace('_', ' ').title())
        
        plt.title('Box Plot: ' + metric.replace('_', ' ').title())
        
        # Set legend for box colors
        legend_patches = [plt.Rectangle((0, 0), 1, 1, facecolor=color) for color in box_colors]
        plt.legend(legend_patches, ['Crawl-accept', 'Crawl-noop'], loc='upper right')
        
        # Save the plot as a PNG image
        output_path = f"{output_folder}/{metric}.png"
        print(f"Table saved as {output_path}")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

    return crawl_data_box_plots

#3. Compare data from two crawls in a table
def table_metrics():
    # Store the box plot data
    crawl_data_box_plots = box_plots_metrics()
    
    # Keep only the first digit
    for crawl, data in crawl_data_box_plots['page_load_time'].items():
        rounded_values = [round(val, 1) for val in data]
        crawl_data_box_plots['page_load_time'][crawl]=rounded_values
   

    # Extract the crawl types and metrics from the dictionary
    crawl_types = list(crawl_data_box_plots['page_load_time'].keys())
    metrics = list(crawl_data_box_plots.keys())

    # Create the table data list
    table_data_list = [
        ["", "", "crawl accept", "", "", "crawl noop", ""],
        ["Metrics", "Min", "Median", "Max", "Min", "Median", "Max"]
    ]

    for metric in metrics:
        row = [
            metric.replace('_', ' ').capitalize(),
            min(crawl_data_box_plots[metric]["crawl-accept"]),
            np.median(crawl_data_box_plots[metric]["crawl-accept"]),
            max(crawl_data_box_plots[metric]["crawl-accept"]),
            min(crawl_data_box_plots[metric]["crawl-noop"]),
            np.median(crawl_data_box_plots[metric]["crawl-noop"]),
            max(crawl_data_box_plots[metric]["crawl-noop"])
        ]
        table_data_list.append(row)

    # Create the table plot
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.axis('off')

    table = ax.table(cellText=table_data_list, loc='center', cellLoc='center')

    # Get the number of rows in the table
    num_rows = len(table_data_list)

    # Apply the formatting to the table cells
    for i in range(0, num_rows):
        table[0, i].get_text().set_fontweight('bold')
        table[1, i].get_text().set_fontweight('bold')

    for i in range(2, num_rows):
        for j in range(1,len(table_data_list[0])):
            table[i,j].get_text().set_horizontalalignment("right")

    for i in range(0,num_rows):
        table[i,0].get_text().set_horizontalalignment("left")

    # Set the width of the cells in the first column
    for row in range(0, num_rows):
        cell = table[row, 0]
        cell.set_width(0.4)

    # Customize the table appearance
    table.auto_set_font_size(False)

    # Adjust the table layout
    table.scale(1, 1.2)
    table.set_fontsize(7)

    # Save the table as a PNG image
    plt.savefig('./analysis/metrics_table.png', bbox_inches='tight', dpi=500)
    plt.close(fig)
    print(f"Table saved as {'./analysis/metrics_table.png'}")
    
table_metrics()

#4. Add a table of ten most prevalent third-party domains
def most_prevalent_third_party_domains():
    # Dictionary to store third-party domains by crawl type
    crawl_domains = defaultdict(list)

    for file in os.listdir(crawl_data):
        if file.endswith("_accept.json") or file.endswith("_noop.json"):
            filepath = os.path.join(crawl_data, file)
            with open(filepath, 'r') as f:
                data = json.load(f)
                crawl_type = "crawl-accept" if file.endswith("_accept.json") else "crawl-noop"
                crawl_domains[crawl_type].extend(data['third_party_request_domains'])

    # Count distinct websites for each third-party domain in each crawl type
    domain_counts = {}
    for crawl_type, domains in crawl_domains.items():
        domain_counts[crawl_type] = Counter(domains)

    # Combine domain counts across crawl types
    combined_counts = Counter()
    for counts in domain_counts.values():
        combined_counts.update(counts)

    # Sort domains by prevalence
    sorted_domains = sorted(combined_counts.items(), key=lambda x: x[1], reverse=True)

    # Create the table 
    table_data = [["Third-Party Domain", "Crawl-Accept", "Crawl-Noop", "IsTracker?"]]
    for domain, count in sorted_domains[:10]:
        is_tracker = "Yes" if domain in data["tracker_domains"] else "No"
        crawl_accept_count = domain_counts["crawl-accept"][domain]
        crawl_noop_count = domain_counts["crawl-noop"][domain]
        table_data.append([domain, crawl_accept_count, crawl_noop_count, is_tracker])

    # Create the table plot
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.axis('off')

    table = ax.table(cellText=table_data, loc='center', cellLoc='center')

    # Apply the formatting to the table cells
    for i in range(0, len(table_data[0])):
        table[0, i].get_text().set_fontweight('bold')

    for i in range(0, len(sorted_domains[:10])+ 1):
        table[i,0].get_text().set_horizontalalignment("left")

    for i in range(1, len(sorted_domains[:10])+ 1):
        for j in range(1, len(table_data[0])):
            table[i, j].get_text().set_horizontalalignment("right")

    # Set the width of the cells in the first column
    for row in range(0, len(table_data)):
        cell = table[row, 0]
        cell.set_width(0.4) 

    # Adjust the table layout
    table.scale(1, 1.5)
    table.set_fontsize(7)

    # Save the table as a PNG file
    output_filename = "third_party_domains.png"
    output_path = f"{output_folder}/{output_filename}"

    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close(fig)

    print(f"Table saved as {output_path}")

most_prevalent_third_party_domains()


#5 Add a scatter plot of Y=number of distinct tracker domains vs. X=website’s Tranco rank
def scatter_plots():
    # Dictionary to store third-party domains by crawl type
    crawl_domains = defaultdict(list)

    tranco_ranks = {}
    with open("tranco-top-500-safe.csv", "r") as csv_file: 
        reader = csv.DictReader(csv_file)
        for row in reader:
            tranco_ranks[row["domain"]] = int(row["tranco_rank"])

    for file in os.listdir(crawl_data):
        if file.endswith("_accept.json") or file.endswith("_noop.json"):
            filepath = os.path.join(crawl_data, file)
            with open(filepath, 'r') as f:
                data = json.load(f)
                crawl_type = "crawl-accept" if file.endswith("_accept.json") else "crawl-noop"
                crawl_domains[crawl_type].extend(data['third_party_request_domains'])

    for crawl_type, domains in crawl_domains.items():
        tracker_domains = set(domains).intersection(set(data["tracker_domains"]))
        tracker_domain_count = len(tracker_domains)

        if tracker_domain_count > 0:
            x = []
            y = []

            for domain in tracker_domains:
                if domain in tranco_ranks:
                    x.append(tranco_ranks[domain])
                    y.append(tracker_domain_count)

            # Create a scatter plot
            plt.scatter(x, y)
            plt.xlabel("Tranco Rank")
            plt.ylabel("Number of Distinct Tracker Domains")
            plt.title(f"{crawl_type} Scatter Plot")

            # Save the scatter plot as an image
            output_filename = f"{crawl_type}_scatter_plot.png"
            output_path = f"{output_folder}/{output_filename}"

            plt.savefig(output_path)
            plt.close()

            print(f"Scatter plot for {crawl_type} saved as {output_path}")
        else:
            print(f"No tracker domains found for {crawl_type}")
            

scatter_plots()

#6.Add a table of top ten tracker entities and their prevalence
def top_ten_tracker_entities():
    # Dictionary to store tracker entities by crawl type
    crawl_domains = defaultdict(list)

    for file in os.listdir(crawl_data):
        if file.endswith("_accept.json") or file.endswith("_noop.json"):
            filepath = os.path.join(crawl_data, file)
            with open(filepath, 'r') as f:
                data = json.load(f)
                crawl_type = "crawl-accept" if file.endswith("_accept.json") else "crawl-noop"
                crawl_domains[crawl_type].extend(data['tracker_entities'])

    # Count distinct websites for each tracker entity in each crawl type
    domain_counts = {}
    for crawl_type, domains in crawl_domains.items():
        domain_counts[crawl_type] = Counter(domains)

    # Combine domain counts across crawl types
    combined_counts = Counter()
    for counts in domain_counts.values():
        combined_counts.update(counts)

    # Sort domains by prevalence
    sorted_domains = sorted(combined_counts.items(), key=lambda x: x[1], reverse=True)

    # Create the table
    table_data = [["Tracker entity", "Crawl-Accept", "Crawl-Noop"]]
    for domain, count in sorted_domains[:10]:
        crawl_accept_count = domain_counts["crawl-accept"][domain]
        crawl_noop_count = domain_counts["crawl-noop"][domain]
        table_data.append([domain, crawl_accept_count, crawl_noop_count])

    # Create the table plot
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.axis('off')

    table = ax.table(cellText=table_data, loc='center', cellLoc='center')

    # Apply the formatting to the table cells
    for i in range(0, len(table_data[0])):
        table[0, i].get_text().set_fontweight('bold')

    for i in range(0, len(sorted_domains[:10])+ 1):
        table[i,0].get_text().set_horizontalalignment("left")

    for i in range(1, len(sorted_domains[:10])+ 1):
        for j in range(1, len(table_data[0])):
            table[i, j].get_text().set_horizontalalignment("right")

    # Set the width of the cells in the first column
    for row in range(0, len(table_data)):
        cell = table[row, 0]
        cell.set_width(0.4)  

    # Adjust the table layout
    table.scale(1, 1.5)
    table.set_fontsize(7)

    # Save the table as a PNG file
    output_filename = "tracker_entities.png" 
    output_path = f"{output_folder}/{output_filename}"

    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close(fig)

    print(f"Table saved as {output_path}")

top_ten_tracker_entities()


#9 Identify ten most common cross-domain HTTP redirection pairs that involve a tracker domain
def most_common_cross_domain():
    # Dictionary to store the tracker domains and cross-domain redirections
    crawl_cross_domain = defaultdict(lambda: defaultdict(list))

    # Iterate over the files in the crawl data folder
    for file in os.listdir(crawl_data):
        if file.endswith(".json"):
            file_path = os.path.join(crawl_data, file)
            with open(file_path, "r") as f:
                data = json.load(f)
                crawl_type = "crawl-accept" if file.endswith("_accept.json") else "crawl-noop"
                crawl_cross_domain[crawl_type]['tracker_domains'].extend(data.get('tracker_domains', []))
                crawl_cross_domain[crawl_type]['x_domain_redirects'].extend(data.get('x_domain_redirects', []))


    # Iterate over crawl types
    for crawl_type, data in crawl_cross_domain.items():
        # Identify the top ten most common redirection pairs for the crawl type
        top_pairs = identify_redirection_pairs(data)

        # Create the table data list
        table_data_list = [["Source domain", "Target domain", "Number of distinct websites"]]
        for pair, count in top_pairs:
            table_data_list.append([pair[0], pair[1], count])

        # Create the figure and axes
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.axis('off')

        # Create the table
        table = ax.table(cellText=table_data_list, loc='center', cellLoc='center')

        # Apply formatting to the table cells
        for i in range(0, len(table_data_list[0])):
            table[0, i].get_text().set_fontweight('bold')

        for i in range(0, len(table_data_list)):
            for j in range(0, len(table_data_list[0])):
                table[i, j].get_text().set_horizontalalignment("left")

        for i in range(0, len(table_data_list)):
            table[i, 2].get_text().set_horizontalalignment("right")

        # Customize the table appearance
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)

        # Set the width of the cells in the first column
        for row in range(0, len(table_data_list)):
            cell = table[row, 2]
            cell.set_width(0.51)  

        # Save the table as a PNG image
        plt.savefig(f"./analysis/redirection_pairs_table_{crawl_type}.png", bbox_inches='tight', dpi=300)
        plt.close(fig)
        print(f"Table saved as ./analysis/redirection_pairs_table_{crawl_type}.png")

# Function to identify the ten most common cross-domain redirection pairs involving a tracker domain
def identify_redirection_pairs(crawl_data):
    all_redirects = crawl_data['x_domain_redirects']
    tracker_domains = crawl_data['tracker_domains']

    redirection_pairs = []
    
    for redirect in all_redirects:
        if redirect != []:
            source_domain = redirect[0]
            target_domain = redirect[1]
            if source_domain in tracker_domains or target_domain in tracker_domains:
                redirection_pairs.append((source_domain, target_domain))

    redirect_counts = Counter(redirection_pairs)
    top_pairs = redirect_counts.most_common(10)
    
    return top_pairs

most_common_cross_domain()